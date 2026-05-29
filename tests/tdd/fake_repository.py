"""
Fake Repository for TDD tests.
This in-memory implementation replaces the real SQLite adapter
so that domain tests remain isolated from infrastructure.
"""

from typing import List, Optional
from src.domain.producto import Producto
from src.ports.producto_repository import IProductoRepository


class FakeProductoRepository(IProductoRepository):
    """In-memory implementation of IProductoRepository for testing."""

    def __init__(self, productos: List[Producto] = None):
        self._productos = {p.id: p for p in (productos or [])}
        self._next_id = max(self._productos.keys(), default=0) + 1

    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        return self._productos.get(producto_id)

    def obtener_por_nombre(self, nombre: str) -> Optional[Producto]:
        for p in self._productos.values():
            if p.nombre.lower() == nombre.lower():
                return p
        return None

    def listar_todos(self) -> List[Producto]:
        return list(self._productos.values())

    def guardar(self, producto: Producto) -> Producto:
        if producto.id is None:
            producto.id = self._next_id
            self._next_id += 1
        self._productos[producto.id] = producto
        return producto

    def actualizar(self, producto: Producto) -> Producto:
        self._productos[producto.id] = producto
        return producto

    def eliminar(self, producto_id: int) -> bool:
        if producto_id in self._productos:
            del self._productos[producto_id]
            return True
        return False
