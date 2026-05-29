"""
Adaptador de IA - Asistente RAG con IA Local
CheckBar - Capa de Adaptadores

Implementa el patron RAG (Retrieval-Augmented Generation):
1. RETRIEVAL: Lee el archivo de conocimiento (recetas y reglas)
2. AUGMENTATION: Inyecta el contexto en el prompt
3. GENERATION: Llama a una API compatible con OpenAI (Ollama/LM Studio)
"""

import os
import httpx
from pathlib import Path
from dotenv import load_dotenv
from src.ports.ai_assistant_port import IAIAssistant

# Cargar variables de entorno, forzando lectura del archivo .env
load_dotenv(override=True)

# Ruta al archivo de conocimiento RAG
KNOWLEDGE_BASE_PATH = Path(__file__).parent / "recetas_y_reglas.txt"


def _load_knowledge_base() -> str:
    """Carga el archivo de conocimiento para el RAG."""
    if not KNOWLEDGE_BASE_PATH.exists():
        raise FileNotFoundError(
            f"Archivo de conocimiento no encontrado: {KNOWLEDGE_BASE_PATH}"
        )
    return KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8")


class LocalAIRAGAssistant(IAIAssistant):
    """
    Implementacion del asistente de IA usando un modelo local (via API compatible OpenAI).
    """

    def __init__(self):
        """Inicializa el cliente con la URL y el modelo del entorno."""
        self._api_url = os.getenv("LOCAL_AI_URL", "http://localhost:11434/v1")
        self._model = os.getenv("LOCAL_AI_MODEL", "qwen2.5:7b")

    def chat(self, pregunta: str) -> str:
        """
        Procesa una pregunta usando el patron RAG y el modelo local.
        """
        if not pregunta or not pregunta.strip():
            return "Por favor, escribe una pregunta para que pueda ayudarte."

        try:
            contexto = _load_knowledge_base()
        except FileNotFoundError as e:
            return f"Error: No se pudo cargar la base de conocimiento. {str(e)}"

        system_prompt, user_prompt = _build_rag_messages(contexto=contexto, pregunta=pregunta)

        # GENERATION - Llamar a la API local (Ollama Nativo /api/generate)
        try:
            # Construimos el endpoint. Si el usuario puso /v1, asumimos OpenAI
            endpoint = f"{self._api_url}/api/generate"
            is_openai = False
            
            if "/v1" in self._api_url:
                endpoint = f"{self._api_url}/chat/completions"
                is_openai = True
                payload = {
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7
                }
            else:
                # Payload para Ollama /api/generate (más compatible con versiones antiguas)
                prompt_text = f"Sistema: {system_prompt}\n\nUsuario: {pregunta}"
                payload = {
                    "model": self._model,
                    "prompt": prompt_text,
                    "stream": False,
                    "options": {"temperature": 0.7}
                }

            response = httpx.post(
                endpoint,
                json=payload,
                timeout=300.0
            )
            response.raise_for_status()
            data = response.json()
            
            if is_openai:
                return data["choices"][0]["message"]["content"]
            else:
                return data.get("response", "Respuesta inesperada de la IA local.")
                
        except httpx.RequestError as e:
            return (
                f"Error al conectar con la IA local en {self._api_url}. "
                f"Asegurate de que el servidor (Ollama/LM Studio) este encendido. "
                f"Detalle técnico: {str(e)}"
            )
        except Exception as e:
            return (
                f"Lo siento, hubo un error inesperado al procesar tu consulta. "
                f"Detalle tecnico: {str(e)}"
            )


def _build_rag_messages(contexto: str, pregunta: str) -> tuple[str, str]:
    """
    Construye los mensajes de sistema y usuario para la IA local.
    """
    system_prompt = f"""Eres el asistente de IA de CheckBar, un sistema de gestion de inventario y cocteleria para un bar de alta calidad. Tu nombre es "Barman AI".

Tu personalidad:
- Eres experto en cocteleria y gestion de bar
- Respondes de manera amigable, profesional y practica
- Usas el conocimiento provisto para dar respuestas precisas
- Si te preguntan algo que no esta en tu base de conocimiento, lo dices honestamente
- Puedes hacer sugerencias basadas en el contexto del bar

BASE DE CONOCIMIENTO DEL BAR (Recetas y Politicas):
===================================================
{contexto}
===================================================

Instrucciones importantes:
1. Responde SIEMPRE en el mismo idioma de la pregunta (espanol preferentemente).
2. Basa tu respuesta en la informacion de la base de conocimiento cuando sea relevante.
3. Para recetas, incluye los ingredientes y pasos de preparacion de manera clara.
4. Para consultas de inventario o politicas, cita las reglas especificas.
5. Si la pregunta no esta cubierta en la base de conocimiento, usa tu conocimiento general de cocteleria pero indica que es informacion general.
6. Mantén las respuestas concisas y practicas para uso en el bar."""

    user_prompt = pregunta
    return system_prompt, user_prompt


def create_assistant() -> LocalAIRAGAssistant:
    """Factory function para crear el asistente de IA."""
    return LocalAIRAGAssistant()
