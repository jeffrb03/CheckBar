"""
Adaptador de IA - Barman AI v4
CheckBar - Capa de Adaptadores

Estrategia en cascada:
  1. Gemini 2.0 Flash (API gratuita, instantáneo) — si GEMINI_API_KEY está configurada
  2. Fallback → Ollama local (qwen2.5:0.5b) — si no hay API key o Gemini falla

Características:
- Memoria de conversación entre turnos
- Acceso al inventario real de la BD
- Prompt anti-alucinaciones (temperatura baja)
- Respuestas rápidas y concisas
"""

import os
import httpx
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from src.ports.ai_assistant_port import IAIAssistant

load_dotenv(override=True)

KNOWLEDGE_BASE_PATH = Path(__file__).parent / "recetas_y_reglas.txt"

# Gemini REST endpoint (no SDK needed, just httpx)
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def _load_knowledge_base() -> str:
    if not KNOWLEDGE_BASE_PATH.exists():
        return ""
    text = KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8")
    return text[:4000] if len(text) > 4000 else text


def _get_inventory_context(db_session) -> str:
    """Consulta el inventario de la BD y lo formatea limpiamente para la IA."""
    try:
        from src.adapters.database import ProductoModel
        productos = db_session.query(ProductoModel).order_by(
            ProductoModel.stock_actual.asc()
        ).all()

        if not productos:
            return "INVENTARIO: Vacío."

        bajos = [p for p in productos if p.stock_actual < p.stock_minimo]
        ok = [p for p in productos if p.stock_actual >= p.stock_minimo]

        lines = ["=== INVENTARIO ACTUAL DEL BAR ==="]

        if bajos:
            lines.append(f"\n⚠️ STOCK BAJO - NECESITAN REPOSICIÓN ({len(bajos)} productos):")
            for p in bajos:
                lines.append(
                    f"  - {p.nombre}: {p.stock_actual} {p.unidad_medida} "
                    f"(mínimo: {p.stock_minimo}) | ${p.precio_unitario:.2f}"
                )
        else:
            lines.append("\n✅ No hay productos con stock bajo.")

        lines.append(f"\n✅ DISPONIBLES ({len(ok)} productos):")
        for p in ok[:20]:
            lines.append(
                f"  - {p.nombre}: {p.stock_actual} {p.unidad_medida} "
                f"| {p.categoria} | ${p.precio_unitario:.2f}"
            )
        if len(ok) > 20:
            lines.append(f"  ... y {len(ok) - 20} productos más disponibles.")

        return "\n".join(lines)
    except Exception as e:
        return f"(Error consultando inventario: {e})"


def _build_system_prompt(db_session) -> str:
    inventory = _get_inventory_context(db_session) if db_session else "Inventario no disponible."
    recipes = _load_knowledge_base()

    return f"""Eres "Barman AI", asistente del sistema CheckBar para gestión de bar premium.

DATOS REALES DEL SISTEMA (úsalos para responder con precisión):
{inventory}

RECETAS DEL BAR (para preguntas sobre cócteles):
{recipes}

INSTRUCCIONES ESTRICTAS:
- Responde SIEMPRE en español, de forma breve y directa (máximo 8 líneas).
- Para preguntas de STOCK o INVENTARIO: usa ÚNICAMENTE los datos del INVENTARIO ACTUAL de arriba. NO inventes productos ni cantidades.
- Para preguntas de RECETAS: usa la sección de recetas del bar.
- Para RECOMENDACIONES: sugiere cócteles usando productos que tengan buen stock.
- NO inventes nombres de productos, precios ni cantidades que no estén en los datos.
- Recuerdas toda la conversación actual."""


class GeminiAssistant:
    """Usa Gemini 2.0 Flash vía REST API (gratis, sin SDK)."""

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._history: List[Dict] = []  # Gemini format: [{role, parts:[{text}]}]
        self._db_session = None

    def set_db_session(self, db_session):
        self._db_session = db_session

    def chat(self, pregunta: str) -> str:
        self._history.append({"role": "user", "parts": [{"text": pregunta}]})
        if len(self._history) > 16:
            self._history = self._history[-16:]

        system_instruction = _build_system_prompt(self._db_session)

        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": self._history,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 512,
                "topP": 0.9,
            }
        }

        try:
            response = httpx.post(
                f"{GEMINI_URL}?key={self._api_key}",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            self._history.append({"role": "model", "parts": [{"text": text}]})
            return text
        except Exception as e:
            raise RuntimeError(f"Gemini error: {e}")

    def clear_history(self):
        self._history = []


class OllamaAssistant:
    """Usa Ollama local vía /api/chat."""

    def __init__(self, api_url: str, model: str):
        self._api_url = api_url.rstrip("/").replace("/v1", "")
        self._model = model
        self._history: List[Dict[str, str]] = []
        self._db_session = None

    def set_db_session(self, db_session):
        self._db_session = db_session

    def chat(self, pregunta: str) -> str:
        self._history.append({"role": "user", "content": pregunta})
        if len(self._history) > 12:
            self._history = self._history[-12:]

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": _build_system_prompt(self._db_session)}
            ] + self._history,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 400}
        }

        response = httpx.post(
            f"{self._api_url}/api/chat",
            json=payload,
            timeout=300.0
        )
        response.raise_for_status()
        respuesta = response.json().get("message", {}).get("content", "").strip()
        if not respuesta:
            respuesta = "No pude generar una respuesta."
        self._history.append({"role": "assistant", "content": respuesta})
        return respuesta

    def clear_history(self):
        self._history = []


class LocalAIRAGAssistant(IAIAssistant):
    """
    Fachada principal: intenta Gemini primero, cae a Ollama si no hay API key.
    Expone la misma interfaz sin importar cuál backend está activo.
    """

    def __init__(self):
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        local_url = os.getenv("LOCAL_AI_URL", "http://localhost:11434")
        local_model = os.getenv("LOCAL_AI_MODEL", "qwen2.5:0.5b")

        if gemini_key:
            self._backend = GeminiAssistant(gemini_key)
            self._backend_name = "Gemini 2.0 Flash"
        else:
            self._backend = OllamaAssistant(local_url, local_model)
            self._backend_name = f"Local ({local_model})"

        self._db_session = None

    def set_db_session(self, db_session):
        self._db_session = db_session
        self._backend.set_db_session(db_session)

    def chat(self, pregunta: str) -> str:
        if not pregunta or not pregunta.strip():
            return "Por favor, escribe una pregunta."
        try:
            return self._backend.chat(pregunta)
        except Exception as e:
            return (
                f"Error al conectar con el asistente de IA. "
                f"Backend: {self._backend_name}. Detalle: {str(e)}"
            )

    def clear_history(self):
        self._backend.clear_history()

    @property
    def backend_name(self) -> str:
        return self._backend_name


def create_assistant() -> LocalAIRAGAssistant:
    return LocalAIRAGAssistant()
