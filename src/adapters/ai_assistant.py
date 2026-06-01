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
            lines.append(f"\n⚠️ STOCK BAJO ({len(bajos)} productos necesitan reposición):")
            for p in bajos:
                lines.append(f"  - {p.nombre}: {p.stock_actual}/{p.stock_minimo} {p.unidad_medida} | ${p.precio_unitario:.0f}")
        else:
            lines.append("\n✅ Sin productos con stock bajo.")

        lines.append(f"\n✅ DISPONIBLES ({len(ok)} productos):")
        # Agrupar por categoría para ser más compacto
        from collections import defaultdict
        por_categoria = defaultdict(list)
        for p in ok:
            por_categoria[p.categoria].append(f"{p.nombre} ({p.stock_actual} {p.unidad_medida}, ${p.precio_unitario:.0f})")
        for cat, items in sorted(por_categoria.items()):
            lines.append(f"  [{cat}]: {', '.join(items)}")

        return "\n".join(lines)
    except Exception as e:
        return f"(Error consultando inventario: {e})"


def _build_system_prompt(db_session) -> str:
    inventory = _get_inventory_context(db_session) if db_session else "Inventario no disponible."
    recipes = _load_knowledge_base()

    return f"""Eres "Barman AI", el asistente oficial de CheckBar.
TIENES ACCESO DIRECTO AL INVENTARIO. Usa los siguientes datos para responder:

{inventory}

RECETAS DEL BAR:
{recipes}

REGLAS DE ORO:
1. Responde siempre en español, de forma breve (máximo 4 líneas).
2. Si te preguntan por inventario o stock, lee los datos de arriba y responde. NUNCA digas que no tienes acceso.
3. No inventes productos ni precios que no estén en la lista.
4. Para recetas, usa la sección de recetas proporcionada."""


class GeminiRateLimitError(Exception):
    """Se lanza cuando Gemini devuelve 429 para activar el fallback a Ollama."""
    pass


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
                "maxOutputTokens": 400,
                "topP": 0.9,
            }
        }

        try:
            response = httpx.post(
                f"{GEMINI_URL}?key={self._api_key}",
                json=payload,
                timeout=30.0
            )
            if response.status_code == 429:
                # Rate limit — activar fallback a Ollama sin mostrar error al usuario
                raise GeminiRateLimitError("Rate limit alcanzado, usando modelo local.")
            response.raise_for_status()
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            self._history.append({"role": "model", "parts": [{"text": text}]})
            return text
        except GeminiRateLimitError:
            raise
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
        if len(self._history) > 6:
            self._history = self._history[-6:]

        context = _get_inventory_context(self._db_session) if self._db_session else ""
        recipes = _load_knowledge_base()
        
        messages = [{"role": "system", "content": "Eres Barman AI. Responde en español y de forma súper corta basándote estrictamente en los datos que te da el usuario."}]
        
        for i, msg in enumerate(self._history):
            if i == len(self._history) - 1:
                # Inyectar el contexto directamente en la última pregunta del usuario (vital para modelos de 0.5b)
                enriched = f"INVENTARIO ACTUAL:\n{context}\n\nRECETAS:\n{recipes}\n\nPREGUNTA DEL USUARIO:\n{msg['content']}"
                messages.append({"role": "user", "content": enriched})
            else:
                messages.append(msg)

        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 300}
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

        # Siempre tener fallback local disponible
        self._ollama = OllamaAssistant(local_url, local_model)
        self._local_model = local_model

        if gemini_key:
            self._backend = GeminiAssistant(gemini_key)
            self._backend_name = "Gemini 2.0 Flash"
        else:
            self._backend = self._ollama
            self._backend_name = f"Local ({local_model})"

        self._db_session = None

    def set_db_session(self, db_session):
        self._db_session = db_session
        self._backend.set_db_session(db_session)
        self._ollama.set_db_session(db_session)

    def chat(self, pregunta: str) -> str:
        if not pregunta or not pregunta.strip():
            return "Por favor, escribe una pregunta."
        try:
            return self._backend.chat(pregunta)
        except Exception as e:
            error_str = str(e)
            # Detectar 429 de cualquier forma (por clase de error o mensaje de texto)
            is_rate_limit = (
                isinstance(e, GeminiRateLimitError) or 
                "429" in error_str or 
                "Too Many Requests" in error_str
            )
            
            if is_rate_limit and isinstance(self._backend, GeminiAssistant):
                # Fallback garantizado a Ollama local
                try:
                    return self._ollama.chat(pregunta)
                except Exception as e_ollama:
                    return f"Gemini alcanzó su límite (429) y el modelo local también falló. Detalle local: {str(e_ollama)}"
            
            return (
                f"Error al conectar con el asistente de IA. "
                f"Backend: {self._backend_name}. Detalle: {error_str}"
            )

    def clear_history(self):
        self._backend.clear_history()
        self._ollama.clear_history()

    @property
    def backend_name(self) -> str:
        return self._backend_name


def create_assistant() -> LocalAIRAGAssistant:
    return LocalAIRAGAssistant()
