"""
Adaptador de IA - Asistente RAG con Google Gemini
CheckBar - Capa de Adaptadores

Implementa el patron RAG (Retrieval-Augmented Generation):
1. RETRIEVAL: Lee el archivo de conocimiento (recetas y reglas)
2. AUGMENTATION: Inyecta el contexto en el prompt
3. GENERATION: Llama a la API de Gemini para generar la respuesta

Requiere la variable de entorno GEMINI_API_KEY configurada en el .env
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from src.ports.ai_assistant_port import IAIAssistant

# Cargar variables de entorno
load_dotenv()

# Ruta al archivo de conocimiento RAG
KNOWLEDGE_BASE_PATH = Path(__file__).parent / "recetas_y_reglas.txt"


def _load_knowledge_base() -> str:
    """
    Carga el archivo de conocimiento para el RAG.
    
    Returns:
        Contenido del archivo como string.
        
    Raises:
        FileNotFoundError: Si el archivo de conocimiento no existe.
    """
    if not KNOWLEDGE_BASE_PATH.exists():
        raise FileNotFoundError(
            f"Archivo de conocimiento no encontrado: {KNOWLEDGE_BASE_PATH}"
        )
    return KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8")


class GeminiRAGAssistant(IAIAssistant):
    """
    Implementacion del asistente de IA usando Google Gemini con patron RAG.
    
    Flujo RAG:
    1. Lee la base de conocimiento (recetas_y_reglas.txt)
    2. Construye un prompt enriquecido con el contexto
    3. Llama a la API de Gemini
    4. Retorna la respuesta generada
    """

    def __init__(self):
        """Inicializa el cliente de Gemini con la API key del entorno."""
        self._api_key = os.getenv("GEMINI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "GEMINI_API_KEY no encontrada. "
                "Configura esta variable en tu archivo .env"
            )
        self._model = None
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Inicializa el cliente de Google Generative AI."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                },
            )
        except ImportError:
            raise ImportError(
                "La libreria 'google-generativeai' no esta instalada. "
                "Ejecuta: pip install google-generativeai"
            )

    def chat(self, pregunta: str) -> str:
        """
        Procesa una pregunta usando el patron RAG.
        
        Paso 1 - RETRIEVAL: Carga la base de conocimiento.
        Paso 2 - AUGMENTATION: Construye el prompt enriquecido.
        Paso 3 - GENERATION: Llama a Gemini API.
        
        Args:
            pregunta: Consulta del bartender o gerente.
            
        Returns:
            Respuesta generada por Gemini contextualizada con el conocimiento del bar.
        """
        if not pregunta or not pregunta.strip():
            return "Por favor, escribe una pregunta para que pueda ayudarte."

        # PASO 1: RETRIEVAL - Cargar base de conocimiento
        try:
            contexto = _load_knowledge_base()
        except FileNotFoundError as e:
            return f"Error: No se pudo cargar la base de conocimiento. {str(e)}"

        # PASO 2: AUGMENTATION - Construir prompt enriquecido
        prompt = _build_rag_prompt(contexto=contexto, pregunta=pregunta)

        # PASO 3: GENERATION - Llamar a la API de Gemini
        try:
            response = self._model.generate_content(prompt)
            return response.text
        except Exception as e:
            return (
                f"Lo siento, hubo un error al procesar tu consulta. "
                f"Detalle tecnico: {str(e)}"
            )


def _build_rag_prompt(contexto: str, pregunta: str) -> str:
    """
    Construye el prompt enriquecido para el patron RAG.
    
    Args:
        contexto: Contenido de la base de conocimiento.
        pregunta: Pregunta del usuario.
        
    Returns:
        Prompt completo listo para enviar a Gemini.
    """
    return f"""Eres el asistente de IA de CheckBar, un sistema de gestion de inventario y cocteleria para un bar de alta calidad. Tu nombre es "Barman AI".

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
6. Mantén las respuestas concisas y practicas para uso en el bar.

PREGUNTA DEL BARTENDER/GERENTE:
{pregunta}

RESPUESTA DE BARMAN AI:"""


def create_assistant() -> GeminiRAGAssistant:
    """
    Factory function para crear el asistente de IA.
    
    Returns:
        Instancia del asistente de IA configurado.
    """
    return GeminiRAGAssistant()
