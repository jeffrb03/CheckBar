"""
Servicio de Dominio: InventarioService
CheckBar - Capa de Dominio

Orquesta la lógica de negocio del inventario.
Solo depende de abstracciones (puertos), nunca de implementaciones concretas.
"""

from typing import List
from src.domain.producto import Producto
from src.domain.venta import Venta, LineaVenta
from src.domain.exceptions import ProductoNoEncontradoError, StockInsuficienteError
from src.ports.producto_repository import IProductoRepository


class InventarioService:
    """
    Servicio de dominio para la gestión de inventario.
    
    Coordina las operaciones de inventario usando el repositorio inyectado.
    No tiene dependencias de infraestructura directas.
    """

    def __init__(self, producto_repository: IProductoRepository):
        """
        Args:
            producto_repository: Implementación del repositorio de productos
                                (puede ser SQLite, in-memory, etc.)
        """
        self._repo = producto_repository

    def obtener_producto(self, producto_id: int) -> Producto:
        """
        Obtiene un producto por ID.
        
        Raises:
            ProductoNoEncontradoError: Si el producto no existe.
        """
        producto = self._repo.obtener_por_id(producto_id)
        if producto is None:
            raise ProductoNoEncontradoError(producto_id=producto_id)
        return producto

    def listar_productos(self) -> List[Producto]:
        """Retorna todos los productos del inventario."""
        return self._repo.listar_todos()

    def obtener_alertas_stock_bajo(self) -> List[Producto]:
        """
        Retorna la lista de productos cuyo stock está por debajo del mínimo.
        
        Regla de negocio: stock_actual < stock_minimo = alerta activa.
        """
        return [p for p in self._repo.listar_todos() if p.tiene_stock_bajo()]

    def registrar_venta(self, lineas: List[LineaVenta], metodo_pago: str = "Efectivo") -> Venta:
        """
        Registra una venta y descuenta el stock de cada producto.
        
        Este método:
        1. Verifica que todos los productos existan.
        2. Verifica que haya suficiente stock para todos.
        3. Descuenta el stock de cada producto.
        4. Retorna la venta creada.
        
        Args:
            lineas: Lista de líneas de venta (producto, cantidad, precio).
            metodo_pago: Medio de pago utilizado.
            
        Returns:
            Objeto Venta con estado "Completada".
            
        Raises:
            ProductoNoEncontradoError: Si algún producto no existe.
            StockInsuficienteError: Si no hay stock suficiente.
        """
        # 1. Verificar que todos los productos existen y tienen stock
        productos_a_actualizar = []
        for linea in lineas:
            producto = self._repo.obtener_por_id(linea.producto_id)
            if producto is None:
                raise ProductoNoEncontradoError(producto_id=linea.producto_id)
            if linea.cantidad > producto.stock_actual:
                raise StockInsuficienteError(
                    producto_nombre=producto.nombre,
                    stock_disponible=producto.stock_actual,
                    cantidad_solicitada=linea.cantidad,
                )
            productos_a_actualizar.append((producto, linea.cantidad))

        # 2. Descontar stock de cada producto (operación atómica conceptual)
        for producto, cantidad in productos_a_actualizar:
            producto.descontar_stock(cantidad)
            self._repo.actualizar(producto)

        # 3. Crear y retornar la venta
        venta = Venta(lineas=lineas, metodo_pago=metodo_pago)
        return venta

    def agregar_producto(self, producto: Producto) -> Producto:
        """
        Agrega un nuevo producto al inventario.
        
        Returns:
            El producto creado con su ID asignado.
        """
        return self._repo.guardar(producto)
