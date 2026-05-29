"""
Entidades Venta y LineaVenta - Capa de Dominio
CheckBar: Sistema de Inventario de Bar

Reglas de negocio:
- Una venta debe tener al menos una línea.
- El total se calcula como la suma de los subtotales de cada línea.
- Una línea de venta registra el precio al momento de la venta (precio histórico).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class LineaVenta:
    """
    Línea de detalle de una venta.
    Representa un producto y su cantidad dentro de una venta.
    """
    producto_id: int
    cantidad: int
    precio_unitario: float

    @property
    def subtotal(self) -> float:
        """Calcula el subtotal de la línea."""
        return round(self.cantidad * self.precio_unitario, 2)

    def to_dict(self) -> dict:
        return {
            "producto_id": self.producto_id,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": self.subtotal,
        }


@dataclass
class Venta:
    """
    Entidad Venta del dominio.
    
    Representa una transacción de venta con todas sus líneas.
    El total se calcula automáticamente como la suma de subtotales.
    """
    lineas: List[LineaVenta]
    metodo_pago: str = "Efectivo"
    id: Optional[int] = None
    numero_factura: str = field(default_factory=lambda: f"FAC-{uuid.uuid4().hex[:8].upper()}")
    fecha_venta: datetime = field(default_factory=datetime.utcnow)
    estado: str = "Completada"
    notas: str = ""

    def __post_init__(self):
        """Valida que la venta tenga al menos una línea."""
        if not self.lineas:
            raise ValueError("La venta debe tener al menos una línea")

    def calcular_total(self) -> float:
        """Calcula el total sumando todos los subtotales."""
        return round(sum(linea.subtotal for linea in self.lineas), 2)

    @property
    def total(self) -> float:
        """Propiedad que retorna el total calculado."""
        return self.calcular_total()

    def cancelar(self) -> None:
        """Cancela la venta cambiando su estado."""
        self.estado = "Cancelada"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "numero_factura": self.numero_factura,
            "fecha_venta": self.fecha_venta.isoformat(),
            "total": self.total,
            "metodo_pago": self.metodo_pago,
            "estado": self.estado,
            "notas": self.notas,
            "lineas": [linea.to_dict() for linea in self.lineas],
        }

    def __str__(self) -> str:
        return (
            f"Venta[{self.numero_factura}] | "
            f"Total: ${self.total:.2f} | "
            f"Estado: {self.estado} | "
            f"Líneas: {len(self.lineas)}"
        )
