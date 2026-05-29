"""
Excepciones del Dominio - CheckBar
Estas excepciones representan errores de negocio puro,
sin dependencias de infraestructura.
"""


class CheckBarDomainError(Exception):
    """Excepción base del dominio CheckBar."""
    pass


class StockInsuficienteError(CheckBarDomainError):
    """Se lanza cuando se intenta descontar más stock del disponible."""
    def __init__(self, producto_nombre: str, stock_disponible: int, cantidad_solicitada: int):
        self.producto_nombre = producto_nombre
        self.stock_disponible = stock_disponible
        self.cantidad_solicitada = cantidad_solicitada
        super().__init__(
            f"Stock insuficiente: solo hay {stock_disponible} unidades disponibles "
            f"de {producto_nombre}, se solicitaron {cantidad_solicitada}."
        )


class ProductoNoEncontradoError(CheckBarDomainError):
    """Se lanza cuando un producto no existe en el repositorio."""
    def __init__(self, producto_id: int = None, nombre: str = None):
        if producto_id is not None:
            msg = f"Producto con ID {producto_id} no encontrado."
        elif nombre:
            msg = f"Producto '{nombre}' no encontrado."
        else:
            msg = "Producto no encontrado."
        super().__init__(msg)


class PrecioInvalidoError(CheckBarDomainError):
    """Se lanza cuando el precio de un producto es inválido (cero o negativo)."""
    def __init__(self, precio: float):
        super().__init__(
            f"El precio unitario debe ser mayor a cero. Valor recibido: {precio}"
        )


class CantidadInvalidaError(CheckBarDomainError):
    """Se lanza cuando una cantidad es cero o negativa."""
    def __init__(self, cantidad: int):
        super().__init__(
            f"La cantidad debe ser mayor a cero. Valor recibido: {cantidad}"
        )


class ProductoDuplicadoError(CheckBarDomainError):
    """Se lanza cuando se intenta registrar un producto con nombre duplicado."""
    def __init__(self, nombre: str):
        super().__init__(f"El producto ya existe en el inventario: '{nombre}'")
