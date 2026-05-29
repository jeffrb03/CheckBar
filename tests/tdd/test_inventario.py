"""
TDD - Test Driven Development: Inventario del Bar
Proyecto: CheckBar
Fase: RED (las pruebas fallan porque el código no existe aún)

Estas pruebas definen el comportamiento esperado del dominio de inventario.
Una vez escritas, se implementará el código mínimo para hacerlas pasar (GREEN).
"""

import pytest
from decimal import Decimal


# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS DEL DOMINIO (aún no existen, por eso es fase RED)
# ─────────────────────────────────────────────────────────────────────────────
from src.domain.producto import Producto
from src.domain.venta import Venta, LineaVenta
from src.domain.inventario_service import InventarioService
from src.domain.exceptions import (
    StockInsuficienteError,
    ProductoNoEncontradoError,
    PrecioInvalidoError,
    CantidadInvalidaError,
)


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def producto_basico():
    """Producto básico para pruebas."""
    return Producto(
        id=1,
        nombre="Vodka Absolut",
        categoria="Licor",
        precio_unitario=75.00,
        precio_costo=40.00,
        stock_actual=20,
        stock_minimo=5,
        unidad_medida="Botella",
        proveedor="Distribuidora Norte",
    )


@pytest.fixture
def producto_stock_bajo():
    """Producto con stock por debajo del mínimo."""
    return Producto(
        id=2,
        nombre="Champagne Moët",
        categoria="Espumoso",
        precio_unitario=350.00,
        precio_costo=200.00,
        stock_actual=3,
        stock_minimo=5,
        unidad_medida="Botella",
        proveedor="Importadora Premium",
    )


@pytest.fixture
def producto_sin_stock():
    """Producto con stock en cero."""
    return Producto(
        id=3,
        nombre="Whisky Macallan 12",
        categoria="Licor",
        precio_unitario=450.00,
        precio_costo=280.00,
        stock_actual=0,
        stock_minimo=2,
        unidad_medida="Botella",
        proveedor="Importadora Premium",
    )


@pytest.fixture
def inventario_service(producto_basico, producto_stock_bajo, producto_sin_stock):
    """Servicio de inventario con repositorio en memoria para pruebas."""
    from tests.tdd.fake_repository import FakeProductoRepository
    repo = FakeProductoRepository([producto_basico, producto_stock_bajo, producto_sin_stock])
    return InventarioService(producto_repository=repo)


# ─────────────────────────────────────────────────────────────────────────────
# TESTS: ENTIDAD PRODUCTO
# ─────────────────────────────────────────────────────────────────────────────

class TestProducto:
    """Pruebas unitarias para la entidad Producto."""

    def test_crear_producto_con_datos_validos(self):
        """Un producto debe crearse correctamente con datos válidos."""
        producto = Producto(
            id=1,
            nombre="Gin Hendricks",
            categoria="Licor",
            precio_unitario=120.00,
            precio_costo=65.00,
            stock_actual=10,
            stock_minimo=3,
            unidad_medida="Botella",
            proveedor="Importadora UK",
        )
        assert producto.nombre == "Gin Hendricks"
        assert producto.precio_unitario == 120.00
        assert producto.stock_actual == 10

    def test_producto_precio_unitario_negativo_lanza_excepcion(self):
        """Un producto con precio negativo debe lanzar PrecioInvalidoError."""
        with pytest.raises(PrecioInvalidoError):
            Producto(
                id=1,
                nombre="Producto Inválido",
                categoria="Licor",
                precio_unitario=-50.00,
                precio_costo=20.00,
                stock_actual=10,
                stock_minimo=2,
                unidad_medida="Botella",
                proveedor="Test",
            )

    def test_producto_precio_cero_lanza_excepcion(self):
        """Un producto con precio cero debe lanzar PrecioInvalidoError."""
        with pytest.raises(PrecioInvalidoError):
            Producto(
                id=1,
                nombre="Producto Cero",
                categoria="Licor",
                precio_unitario=0.0,
                precio_costo=0.0,
                stock_actual=5,
                stock_minimo=1,
                unidad_medida="Botella",
                proveedor="Test",
            )

    def test_producto_stock_negativo_lanza_excepcion(self):
        """Un producto con stock negativo no debe ser válido."""
        with pytest.raises(CantidadInvalidaError):
            Producto(
                id=1,
                nombre="Stock Negativo",
                categoria="Licor",
                precio_unitario=50.00,
                precio_costo=25.00,
                stock_actual=-1,
                stock_minimo=2,
                unidad_medida="Botella",
                proveedor="Test",
            )

    def test_producto_tiene_stock_bajo_cuando_esta_por_debajo_del_minimo(
        self, producto_stock_bajo
    ):
        """tiene_stock_bajo() debe retornar True si stock < stock_minimo."""
        assert producto_stock_bajo.tiene_stock_bajo() is True

    def test_producto_no_tiene_stock_bajo_cuando_esta_por_encima_del_minimo(
        self, producto_basico
    ):
        """tiene_stock_bajo() debe retornar False si stock >= stock_minimo."""
        assert producto_basico.tiene_stock_bajo() is False

    def test_producto_exactamente_en_minimo_no_tiene_stock_bajo(self):
        """Producto con stock == stock_minimo no debe tener alerta."""
        producto = Producto(
            id=1,
            nombre="Ron Bacardí",
            categoria="Licor",
            precio_unitario=55.00,
            precio_costo=30.00,
            stock_actual=5,
            stock_minimo=5,
            unidad_medida="Botella",
            proveedor="Distribuidora Sur",
        )
        assert producto.tiene_stock_bajo() is False

    def test_descontar_stock_reduce_cantidad_correctamente(self, producto_basico):
        """descontar_stock() debe reducir el stock_actual."""
        producto_basico.descontar_stock(3)
        assert producto_basico.stock_actual == 17

    def test_descontar_mas_stock_del_disponible_lanza_excepcion(self, producto_basico):
        """Descontar más stock del disponible debe lanzar StockInsuficienteError."""
        with pytest.raises(StockInsuficienteError):
            producto_basico.descontar_stock(25)  # Solo hay 20

    def test_descontar_stock_cero_lanza_excepcion(self, producto_basico):
        """Descontar cantidad cero o negativa debe lanzar CantidadInvalidaError."""
        with pytest.raises(CantidadInvalidaError):
            producto_basico.descontar_stock(0)

    def test_reponer_stock_aumenta_cantidad(self, producto_basico):
        """reponer_stock() debe aumentar el stock_actual."""
        stock_inicial = producto_basico.stock_actual
        producto_basico.reponer_stock(10)
        assert producto_basico.stock_actual == stock_inicial + 10

    def test_calcular_margen_ganancia(self, producto_basico):
        """El margen de ganancia debe calcularse correctamente."""
        # Vodka Absolut: precio 75, costo 40
        # Margen = (75 - 40) / 75 * 100 = 46.67%
        margen = producto_basico.calcular_margen_ganancia()
        assert round(margen, 2) == 46.67

    def test_producto_representacion_string(self, producto_basico):
        """La representación string del producto debe incluir nombre y stock."""
        repr_str = str(producto_basico)
        assert "Vodka Absolut" in repr_str
        assert "20" in repr_str


# ─────────────────────────────────────────────────────────────────────────────
# TESTS: SERVICIO DE INVENTARIO
# ─────────────────────────────────────────────────────────────────────────────

class TestInventarioService:
    """Pruebas para el servicio de dominio InventarioService."""

    def test_obtener_producto_existente(self, inventario_service):
        """Debe retornar el producto si existe en el repositorio."""
        producto = inventario_service.obtener_producto(1)
        assert producto is not None
        assert producto.nombre == "Vodka Absolut"

    def test_obtener_producto_no_existente_lanza_excepcion(self, inventario_service):
        """Debe lanzar ProductoNoEncontradoError si el producto no existe."""
        with pytest.raises(ProductoNoEncontradoError):
            inventario_service.obtener_producto(999)

    def test_listar_todos_los_productos(self, inventario_service):
        """Debe retornar todos los productos del repositorio."""
        productos = inventario_service.listar_productos()
        assert len(productos) == 3

    def test_listar_productos_con_stock_bajo(self, inventario_service):
        """Debe retornar solo los productos con stock bajo el mínimo."""
        alertas = inventario_service.obtener_alertas_stock_bajo()
        assert len(alertas) >= 1
        nombres = [p.nombre for p in alertas]
        assert "Champagne Moët" in nombres

    def test_registrar_venta_descuenta_stock(self, inventario_service):
        """Registrar una venta debe descontar el stock del producto."""
        lineas = [LineaVenta(producto_id=1, cantidad=5, precio_unitario=75.00)]
        inventario_service.registrar_venta(lineas=lineas)
        producto = inventario_service.obtener_producto(1)
        assert producto.stock_actual == 15  # 20 - 5

    def test_registrar_venta_retorna_objeto_venta(self, inventario_service):
        """registrar_venta() debe retornar un objeto Venta."""
        lineas = [LineaVenta(producto_id=1, cantidad=2, precio_unitario=75.00)]
        venta = inventario_service.registrar_venta(lineas=lineas)
        assert isinstance(venta, Venta)
        assert venta.estado == "Completada"

    def test_registrar_venta_calcula_total_correctamente(self, inventario_service):
        """El total de la venta debe ser la suma de subtotales."""
        lineas = [LineaVenta(producto_id=1, cantidad=3, precio_unitario=75.00)]
        venta = inventario_service.registrar_venta(lineas=lineas)
        assert venta.total == 225.00  # 3 * 75

    def test_registrar_venta_sin_stock_suficiente_lanza_excepcion(
        self, inventario_service
    ):
        """Una venta que supera el stock disponible debe lanzar StockInsuficienteError."""
        lineas = [LineaVenta(producto_id=1, cantidad=999, precio_unitario=75.00)]
        with pytest.raises(StockInsuficienteError):
            inventario_service.registrar_venta(lineas=lineas)

    def test_registrar_venta_con_producto_sin_stock_lanza_excepcion(
        self, inventario_service
    ):
        """Una venta de un producto con stock 0 debe lanzar StockInsuficienteError."""
        lineas = [LineaVenta(producto_id=3, cantidad=1, precio_unitario=450.00)]
        with pytest.raises(StockInsuficienteError):
            inventario_service.registrar_venta(lineas=lineas)

    def test_stock_bajo_despues_de_venta_genera_alerta(self, inventario_service):
        """Después de una venta que deja el stock bajo, debe aparecer en alertas."""
        # Vodka Absolut: stock 20, mínimo 5. Vendemos 16 → stock = 4 < 5
        lineas = [LineaVenta(producto_id=1, cantidad=16, precio_unitario=75.00)]
        inventario_service.registrar_venta(lineas=lineas)
        alertas = inventario_service.obtener_alertas_stock_bajo()
        nombres = [p.nombre for p in alertas]
        assert "Vodka Absolut" in nombres


# ─────────────────────────────────────────────────────────────────────────────
# TESTS: ENTIDAD VENTA
# ─────────────────────────────────────────────────────────────────────────────

class TestVenta:
    """Pruebas para la entidad Venta."""

    def test_crear_venta_con_lineas(self):
        """Una venta debe crearse correctamente con sus líneas."""
        lineas = [
            LineaVenta(producto_id=1, cantidad=2, precio_unitario=75.00),
            LineaVenta(producto_id=2, cantidad=1, precio_unitario=350.00),
        ]
        venta = Venta(lineas=lineas, metodo_pago="Efectivo")
        assert len(venta.lineas) == 2
        assert venta.metodo_pago == "Efectivo"

    def test_total_venta_calculado_correctamente(self):
        """El total debe ser la suma de los subtotales de cada línea."""
        lineas = [
            LineaVenta(producto_id=1, cantidad=2, precio_unitario=75.00),  # 150
            LineaVenta(producto_id=2, cantidad=1, precio_unitario=350.00),  # 350
        ]
        venta = Venta(lineas=lineas, metodo_pago="Tarjeta")
        assert venta.calcular_total() == 500.00

    def test_venta_sin_lineas_lanza_excepcion(self):
        """Una venta sin líneas debe lanzar un error."""
        with pytest.raises(ValueError, match="La venta debe tener al menos una línea"):
            Venta(lineas=[], metodo_pago="Efectivo")

    def test_linea_venta_calcula_subtotal(self):
        """El subtotal de una línea debe ser cantidad * precio_unitario."""
        linea = LineaVenta(producto_id=1, cantidad=3, precio_unitario=75.00)
        assert linea.subtotal == 225.00

    def test_venta_estado_inicial_es_completada(self):
        """El estado inicial de una venta creada debe ser 'Completada'."""
        lineas = [LineaVenta(producto_id=1, cantidad=1, precio_unitario=75.00)]
        venta = Venta(lineas=lineas, metodo_pago="Efectivo")
        assert venta.estado == "Completada"
