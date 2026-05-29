"""
Adaptador de Base de Datos - SQLite + SQLAlchemy
CheckBar - Capa de Adaptadores

Implementa los puertos IProductoRepository e IVentaRepository
usando SQLite como motor de persistencia y SQLAlchemy como ORM.
"""

import os
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, create_engine, text
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker, relationship

from src.domain.producto import Producto
from src.domain.venta import Venta, LineaVenta
from src.ports.producto_repository import IProductoRepository

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE LA BASE DE DATOS
# ─────────────────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./checkbar.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necesario para SQLite con FastAPI
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─────────────────────────────────────────────────────────────────────────────
# MODELOS ORM (SQLAlchemy)
# ─────────────────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


class ProductoModel(Base):
    """Modelo ORM para la tabla productos."""
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(200), unique=True, nullable=False, index=True)
    categoria = Column(String(100), nullable=False)
    precio_unitario = Column(Float, nullable=False)
    precio_costo = Column(Float, nullable=False)
    stock_actual = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=5)
    unidad_medida = Column(String(50), nullable=False, default="Botella")
    proveedor = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    lineas_venta = relationship("LineaVentaModel", back_populates="producto")
    movimientos = relationship("MovimientoInventarioModel", back_populates="producto")


class VentaModel(Base):
    """Modelo ORM para la tabla ventas."""
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    numero_factura = Column(String(50), unique=True, nullable=False)
    fecha_venta = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, nullable=False)
    metodo_pago = Column(String(50), default="Efectivo")
    estado = Column(String(50), default="Completada")
    notas = Column(String(500), default="")

    # Relaciones
    lineas = relationship("LineaVentaModel", back_populates="venta", cascade="all, delete-orphan")


class LineaVentaModel(Base):
    """Modelo ORM para las líneas de venta."""
    __tablename__ = "lineas_venta"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Relaciones
    venta = relationship("VentaModel", back_populates="lineas")
    producto = relationship("ProductoModel", back_populates="lineas_venta")


class MovimientoInventarioModel(Base):
    """Modelo ORM para el registro de movimientos de inventario."""
    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'entrada', 'salida', 'ajuste'
    cantidad = Column(Integer, nullable=False)
    motivo = Column(String(200), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=True)

    # Relación
    producto = relationship("ProductoModel", back_populates="movimientos")


def create_tables():
    """Crea todas las tablas en la base de datos."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Generador de sesiones de base de datos para FastAPI.
    Uso con Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# MAPPERS: ORM → Dominio | Dominio → ORM
# ─────────────────────────────────────────────────────────────────────────────

def orm_to_producto(model: ProductoModel) -> Producto:
    """Convierte un modelo ORM a una entidad de dominio Producto."""
    return Producto(
        id=model.id,
        nombre=model.nombre,
        categoria=model.categoria,
        precio_unitario=model.precio_unitario,
        precio_costo=model.precio_costo,
        stock_actual=model.stock_actual,
        stock_minimo=model.stock_minimo,
        unidad_medida=model.unidad_medida,
        proveedor=model.proveedor or "",
    )


def producto_to_orm(producto: Producto, model: ProductoModel = None) -> ProductoModel:
    """Convierte una entidad de dominio Producto a modelo ORM."""
    if model is None:
        model = ProductoModel()
    model.nombre = producto.nombre
    model.categoria = producto.categoria
    model.precio_unitario = producto.precio_unitario
    model.precio_costo = producto.precio_costo
    model.stock_actual = producto.stock_actual
    model.stock_minimo = producto.stock_minimo
    model.unidad_medida = producto.unidad_medida
    model.proveedor = producto.proveedor
    return model


# ─────────────────────────────────────────────────────────────────────────────
# IMPLEMENTACIÓN DEL REPOSITORIO
# ─────────────────────────────────────────────────────────────────────────────

class SQLiteProductoRepository(IProductoRepository):
    """
    Implementación concreta de IProductoRepository usando SQLite + SQLAlchemy.
    """

    def __init__(self, db: Session):
        self._db = db

    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        model = self._db.query(ProductoModel).filter(ProductoModel.id == producto_id).first()
        return orm_to_producto(model) if model else None

    def obtener_por_nombre(self, nombre: str) -> Optional[Producto]:
        model = self._db.query(ProductoModel).filter(
            ProductoModel.nombre.ilike(nombre)
        ).first()
        return orm_to_producto(model) if model else None

    def listar_todos(self) -> List[Producto]:
        models = self._db.query(ProductoModel).order_by(ProductoModel.nombre).all()
        return [orm_to_producto(m) for m in models]

    def guardar(self, producto: Producto) -> Producto:
        model = producto_to_orm(producto)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        producto.id = model.id
        return producto

    def actualizar(self, producto: Producto) -> Producto:
        model = self._db.query(ProductoModel).filter(ProductoModel.id == producto.id).first()
        if model:
            producto_to_orm(producto, model)
            self._db.commit()
            self._db.refresh(model)
        return producto

    def eliminar(self, producto_id: int) -> bool:
        model = self._db.query(ProductoModel).filter(ProductoModel.id == producto_id).first()
        if model:
            self._db.delete(model)
            self._db.commit()
            return True
        return False


class SQLiteVentaRepository:
    """Repositorio de ventas para SQLite."""

    def __init__(self, db: Session):
        self._db = db

    def guardar(self, venta: Venta) -> Venta:
        """Persiste una venta y sus líneas en la base de datos."""
        venta_model = VentaModel(
            numero_factura=venta.numero_factura,
            fecha_venta=venta.fecha_venta,
            total=venta.total,
            metodo_pago=venta.metodo_pago,
            estado=venta.estado,
            notas=venta.notas,
        )
        self._db.add(venta_model)
        self._db.flush()  # Para obtener el ID de la venta

        for linea in venta.lineas:
            linea_model = LineaVentaModel(
                venta_id=venta_model.id,
                producto_id=linea.producto_id,
                cantidad=linea.cantidad,
                precio_unitario=linea.precio_unitario,
                subtotal=linea.subtotal,
            )
            self._db.add(linea_model)

        self._db.commit()
        self._db.refresh(venta_model)
        venta.id = venta_model.id
        return venta

    def listar_todas(self) -> List[dict]:
        """Lista todas las ventas con sus líneas."""
        models = self._db.query(VentaModel).order_by(VentaModel.fecha_venta.desc()).all()
        return [
            {
                "id": m.id,
                "numero_factura": m.numero_factura,
                "fecha_venta": m.fecha_venta.isoformat() if m.fecha_venta else None,
                "total": m.total,
                "metodo_pago": m.metodo_pago,
                "estado": m.estado,
                "lineas": [
                    {
                        "producto_id": l.producto_id,
                        "cantidad": l.cantidad,
                        "precio_unitario": l.precio_unitario,
                        "subtotal": l.subtotal,
                    }
                    for l in m.lineas
                ],
            }
            for m in models
        ]
