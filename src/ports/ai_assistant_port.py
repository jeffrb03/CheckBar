"""
Puerto: IAIAssistant
CheckBar - Capa de Puertos

Define el contrato abstracto que cualquier implementación de
asistente IA debe cumplir.
"""

from abc import ABC, abstractmethod


class IAIAssistant(ABC):
    """
    Interfaz abstracta para el asistente de IA.
    
    Permite intercambiar entre diferentes proveedores de IA
    (Gemini, OpenAI, Anthropic, etc.) sin modificar la lógica de negocio.
    """

    @abstractmethod
    def chat(self, pregunta: str) -> str:
        """
        Procesa una pregunta del usuario y retorna una respuesta.
        
        Args:
            pregunta: La consulta del bartender o gerente.
            
        Returns:
            Respuesta generada por el modelo de IA.
        """
        ...
