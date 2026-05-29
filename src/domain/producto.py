"""
Entidad Producto - Capa de Dominio
CheckBar: Sistema de Inventario de Bar

Reglas de negocio encapsuladas:
- El precio unitario debe ser mayor a cero.
- El precio de costo debe ser mayor a cero.
- El stock no puede ser negativo.
- Se puede calcular el margen de ganancia.
- Se puede verificar si el stock está por debajo del mínimo.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from src.domain.exceptions import (
    PrecioInvalidoError,
    CantidadInvalidaError,
    StockInsuficienteError,
)


@dataclass
class Producto:
    """
    Entidad central del dominio de inventario.
    
    Representa un producto del bar (licor, mezclador, garnish, etc.)
    con toda la lógica de negocio encapsulada.
    """

    nombre: str
    categoria: str
    precio_unitario: float
    precio_costo: float
    stock_actual: int
    stock_minimo: int
    unidad_medida: str
    proveedor: str
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validaciones de dominio ejecutadas al crear la entidad."""
        self._validar_precios()
        self._validar_stock()

    def _validar_precios(self):
        """El precio unitario y costo deben ser positivos."""
        if self.precio_unitario <= 0:
            raise PrecioInvalidoError(self.precio_unitario)
        if self.precio_costo <= 0:
            raise PrecioInvalidoError(self.precio_costo)

    def _validar_stock(self):
        """El stock no puede ser negativo."""
        if self.stock_actual < 0:
            raise CantidadInvalidaError(self.stock_actual)

    def tiene_stock_bajo(self) -> bool:
        """
        Retorna True si el stock actual está por debajo del mínimo configurado.
        
        Regla de negocio: stock_actual < stock_minimo genera alerta.
        Si stock_actual == stock_minimo, NO hay alerta.
        """
        return self.stock_actual < self.stock_minimo

    def descontar_stock(self, cantidad: int) -> None:
        """
        Descuenta una cantidad del stock actual.
        
        Args:
            cantidad: Número de unidades a descontar.
            
        Raises:
            CantidadInvalidaError: Si la cantidad es <= 0.
            StockInsuficienteError: Si no hay suficiente stock.
        """
        if cantidad <= 0:
            raise CantidadInvalidaError(cantidad)
        if cantidad > self.stock_actual:
            raise StockInsuficienteError(
                producto_nombre=self.nombre,
                stock_disponible=self.stock_actual,
                cantidad_solicitada=cantidad,
            )
        self.stock_actual -= cantidad
        self.updated_at = datetime.utcnow()

    def reponer_stock(self, cantidad: int) -> None:
        """
        Agrega unidades al stock actual.
        
        Args:
            cantidad: Número de unidades a agregar.
            
        Raises:
            CantidadInvalidaError: Si la cantidad es <= 0.
        """
        if cantidad <= 0:
            raise CantidadInvalidaError(cantidad)
        self.stock_actual += cantidad
        self.updated_at = datetime.utcnow()

    def calcular_margen_ganancia(self) -> float:
        """
        Calcula el margen de ganancia bruta en porcentaje.
        
        Fórmula: ((precio_unitario - precio_costo) / precio_unitario) * 100
        
        Returns:
            Margen como porcentaje redondeado a 2 decimales.
        """
        if self.precio_unitario == 0:
            return 0.0
        margen = ((self.precio_unitario - self.precio_costo) / self.precio_unitario) * 100
        return round(margen, 2)

    def __str__(self) -> str:
        """Representación legible del producto."""
        alerta = " ⚠️ STOCK BAJO" if self.tiene_stock_bajo() else ""
        return (
            f"Producto[{self.id}] {self.nombre} | "
            f"Stock: {self.stock_actual} {self.unidad_medida} | "
            f"Precio: ${self.precio_unitario:.2f}{alerta}"
        )

    def __repr__(self) -> str:
        return f"Producto(id={self.id}, nombre='{self.nombre}', stock={self.stock_actual})"

    def to_dict(self) -> dict:
        """Serializa el producto a un diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio_unitario": self.precio_unitario,
            "precio_costo": self.precio_costo,
            "stock_actual": self.stock_actual,
            "stock_minimo": self.stock_minimo,
            "unidad_medida": self.unidad_medida,
            "proveedor": self.proveedor,
            "tiene_stock_bajo": self.tiene_stock_bajo(),
            "margen_ganancia": self.calcular_margen_ganancia(),
        }
