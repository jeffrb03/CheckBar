"""
Puerto: IProductoRepository
CheckBar - Capa de Puertos

Define el contrato abstracto que cualquier implementación de
persistencia de productos debe cumplir.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.producto import Producto


class IProductoRepository(ABC):
    """
    Interfaz abstracta para el repositorio de productos.
    
    El dominio depende de esta abstracción, no de implementaciones concretas.
    Esto permite intercambiar SQLite por PostgreSQL, MongoDB, etc. sin
    tocar la lógica de negocio.
    """

    @abstractmethod
    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        """Obtiene un producto por su ID. Retorna None si no existe."""
        ...

    @abstractmethod
    def obtener_por_nombre(self, nombre: str) -> Optional[Producto]:
        """Obtiene un producto por su nombre. Retorna None si no existe."""
        ...

    @abstractmethod
    def listar_todos(self) -> List[Producto]:
        """Retorna todos los productos del inventario."""
        ...

    @abstractmethod
    def guardar(self, producto: Producto) -> Producto:
        """
        Persiste un producto nuevo.
        
        Returns:
            El producto con su ID asignado por la base de datos.
        """
        ...

    @abstractmethod
    def actualizar(self, producto: Producto) -> Producto:
        """
        Actualiza un producto existente.
        
        Returns:
            El producto actualizado.
        """
        ...

    @abstractmethod
    def eliminar(self, producto_id: int) -> bool:
        """
        Elimina un producto por ID.
        
        Returns:
            True si fue eliminado, False si no existía.
        """
        ...
