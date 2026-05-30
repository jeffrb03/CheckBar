"""
CheckBar - Backend FastAPI
Punto de entrada principal de la aplicacion.

Endpoints:
- GET  /            -> Sirve el frontend (index.html)
- GET  /productos   -> Lista todos los productos del inventario
- POST /ventas      -> Registra una nueva venta
- POST /chat        -> Asistente IA con RAG

Arquitectura Hexagonal:
- FastAPI actua como adaptador de entrada (driving adapter)
- Inyecta los repositorios SQLite en los servicios de dominio
"""

import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Importaciones de la arquitectura hexagonal
from src.adapters.database import (
    create_tables,
    get_db,
    SQLiteProductoRepository,
    SQLiteVentaRepository,
)
from src.domain.inventario_service import InventarioService
from src.domain.producto import Producto
from src.domain.venta import LineaVenta
from src.domain.exceptions import (
    StockInsuficienteError,
    ProductoNoEncontradoError,
    PrecioInvalidoError,
    CantidadInvalidaError,
)


# ─────────────────────────────────────────────────────────────────────────────
# LIFESPAN (Startup/Shutdown)
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializacion y limpieza de la aplicacion."""
    # Startup: crear tablas si no existen
    create_tables()
    print("[CheckBar] Base de datos inicializada correctamente.")
    yield
    # Shutdown (nada que limpiar por ahora)
    print("[CheckBar] Servidor detenido.")


# ─────────────────────────────────────────────────────────────────────────────
# INSTANCIA FASTAPI
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CheckBar API",
    description="""
    **CheckBar** - Sistema de Inventario y Facturacion de Bar con Asistente IA.
    
    ## Endpoints
    
    * **GET /productos** - Lista todos los productos del inventario con estado de stock
    * **POST /ventas** - Registra una nueva venta y descuenta el inventario
    * **POST /chat** - Asistente Barman AI con RAG (Retrieval-Augmented Generation)
    
    ## Arquitectura
    
    Este sistema usa Arquitectura Hexagonal (Ports & Adapters):
    - **Dominio**: Logica de negocio pura (Producto, Venta, InventarioService)
    - **Puertos**: Interfaces abstractas (IProductoRepository, IAIAssistant)
    - **Adaptadores**: SQLite, Gemini API, FastAPI HTTP
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# SCHEMAS PYDANTIC (DTOs de entrada/salida)
# ─────────────────────────────────────────────────────────────────────────────

class ProductoResponse(BaseModel):
    """Schema de respuesta para un producto."""
    id: int
    nombre: str
    categoria: str
    precio_unitario: float
    precio_costo: float
    stock_actual: int
    stock_minimo: int
    unidad_medida: str
    proveedor: str
    tiene_stock_bajo: bool
    margen_ganancia: float

    class Config:
        from_attributes = True


class LineaVentaRequest(BaseModel):
    """Schema de entrada para una linea de venta."""
    producto_id: int = Field(..., gt=0, description="ID del producto")
    cantidad: int = Field(..., gt=0, description="Cantidad a vender")
    precio_unitario: float = Field(..., gt=0, description="Precio unitario al momento de venta")


class VentaRequest(BaseModel):
    """Schema de entrada para registrar una nueva venta."""
    lineas: List[LineaVentaRequest] = Field(
        ..., min_length=1, description="Lineas de la venta (minimo 1)"
    )
    metodo_pago: str = Field(default="Efectivo", description="Metodo de pago")


class VentaResponse(BaseModel):
    """Schema de respuesta para una venta registrada."""
    id: Optional[int]
    numero_factura: str
    fecha_venta: str
    total: float
    metodo_pago: str
    estado: str
    lineas: List[dict]


class ProductoRequest(BaseModel):
    """Schema de entrada para crear un nuevo producto."""
    nombre: str = Field(..., min_length=1)
    categoria: str = Field(..., min_length=1)
    precio_unitario: float = Field(..., gt=0)
    precio_costo: float = Field(..., gt=0)
    stock_actual: int = Field(..., ge=0)
    stock_minimo: int = Field(..., ge=0)
    unidad_medida: str = Field(..., min_length=1)
    proveedor: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    """Schema de entrada para el asistente IA."""
    pregunta: str = Field(..., min_length=1, description="Pregunta al asistente")


class ChatResponse(BaseModel):
    """Schema de respuesta del asistente IA."""
    respuesta: str
    pregunta: str


class ErrorResponse(BaseModel):
    """Schema de error estandarizado."""
    error: str
    detalle: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# DEPENDENCIAS DE INYECCION
# ─────────────────────────────────────────────────────────────────────────────

def get_inventario_service(db: Session = Depends(get_db)) -> InventarioService:
    """Inyecta el servicio de inventario con el repositorio SQLite."""
    repo = SQLiteProductoRepository(db)
    return InventarioService(producto_repository=repo)


def get_ai_assistant():
    """Inyecta el asistente de IA (RAG con Gemini)."""
    try:
        from src.adapters.ai_assistant import create_assistant
        return create_assistant()
    except (ValueError, ImportError, Exception):
        return None  # Libreria no instalada o API key faltante


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get(
    "/productos",
    response_model=List[ProductoResponse],
    summary="Listar productos del inventario",
    tags=["Inventario"],
)
async def get_productos(
    service: InventarioService = Depends(get_inventario_service),
):
    """
    Retorna todos los productos del inventario con su estado de stock.
    
    Incluye:
    - Informacion basica del producto
    - Stock actual vs minimo
    - Indicador de stock bajo (alerta)
    - Margen de ganancia calculado
    """
    productos = service.listar_productos()
    return [p.to_dict() for p in productos]


@app.post(
    "/productos",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Añadir un nuevo producto",
    tags=["Inventario"],
)
async def post_producto(
    producto_request: ProductoRequest,
    service: InventarioService = Depends(get_inventario_service),
):
    """Registra un nuevo producto en el inventario."""
    try:
        nuevo_producto = Producto(
            nombre=producto_request.nombre,
            categoria=producto_request.categoria,
            precio_unitario=producto_request.precio_unitario,
            precio_costo=producto_request.precio_costo,
            stock_actual=producto_request.stock_actual,
            stock_minimo=producto_request.stock_minimo,
            unidad_medida=producto_request.unidad_medida,
            proveedor=producto_request.proveedor,
        )
        producto_guardado = service.agregar_producto(nuevo_producto)
        return producto_guardado.to_dict()
    except (CantidadInvalidaError, PrecioInvalidoError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.get(
    "/ventas",
    response_model=List[VentaResponse],
    summary="Listar historial de ventas",
    tags=["Ventas"],
)
async def get_ventas(db: Session = Depends(get_db)):
    """
    Retorna todo el historial de ventas registradas.
    """
    venta_repo = SQLiteVentaRepository(db)
    ventas = venta_repo.listar_todas()
    return ventas


@app.post(
    "/ventas",
    response_model=VentaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva venta",
    tags=["Ventas"],
)
async def post_venta(
    venta_request: VentaRequest,
    db: Session = Depends(get_db),
    service: InventarioService = Depends(get_inventario_service),
):
    """
    Registra una nueva venta y descuenta el inventario automaticamente.
    
    El sistema:
    1. Verifica que todos los productos existan
    2. Verifica que haya stock suficiente
    3. Descuenta el stock de cada producto
    4. Persiste la venta en la base de datos
    5. Retorna la venta creada con numero de factura
    
    Raises:
        404: Si algun producto no existe
        422: Si no hay stock suficiente
    """
    try:
        # Convertir DTOs a entidades de dominio
        lineas = [
            LineaVenta(
                producto_id=l.producto_id,
                cantidad=l.cantidad,
                precio_unitario=l.precio_unitario,
            )
            for l in venta_request.lineas
        ]

        # Registrar venta en el dominio (descuenta stock)
        venta = service.registrar_venta(lineas=lineas, metodo_pago=venta_request.metodo_pago)

        # Persistir la venta en la BD
        venta_repo = SQLiteVentaRepository(db)
        venta_guardada = venta_repo.guardar(venta)

        return venta_guardada.to_dict()

    except ProductoNoEncontradoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except StockInsuficienteError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except (CantidadInvalidaError, PrecioInvalidoError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.post(
    "/chat",
    response_model=ChatResponse,
    summary="Asistente Barman AI (RAG)",
    tags=["IA"],
)
async def post_chat(
    chat_request: ChatRequest,
):
    """
    Asistente de inteligencia artificial para el bar.
    
    Usa el patron RAG (Retrieval-Augmented Generation):
    1. Recupera el conocimiento del bar (recetas, politicas)
    2. Enriquece el prompt con ese contexto
    3. Genera una respuesta usando Google Gemini
    
    El asistente puede responder sobre:
    - Recetas de cocteleria (Mojito, Margarita, Old Fashioned, etc.)
    - Politicas de inventario
    - Recomendaciones de preparacion
    - Preguntas sobre ingredientes y tecnicas
    
    Requiere que GEMINI_API_KEY este configurado en el .env
    """
    pregunta = chat_request.pregunta

    # Obtener el asistente (puede ser None si no hay API key)
    assistant = get_ai_assistant()

    if assistant is None:
        # Respuesta de fallback si no hay API key configurada
        return ChatResponse(
            pregunta=pregunta,
            respuesta=(
                "El asistente IA no esta configurado. "
                "Por favor configura la variable GEMINI_API_KEY en tu archivo .env "
                "y reinicia el servidor."
            )
        )

    try:
        respuesta = assistant.chat(pregunta)
        return ChatResponse(pregunta=pregunta, respuesta=respuesta)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error en el servicio de IA: {str(e)}",
        )


@app.get(
    "/health",
    summary="Health check",
    tags=["Sistema"],
)
async def health_check():
    """Verifica que la API este funcionando correctamente."""
    return {"status": "ok", "sistema": "CheckBar", "version": "1.0.0"}


# ─────────────────────────────────────────────────────────────────────────────
# ARCHIVOS ESTATICOS (Frontend)
# ─────────────────────────────────────────────────────────────────────────────

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adapters", "static")

# Montar archivos estaticos si el directorio existe
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        """Sirve el archivo index.html del frontend."""
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return JSONResponse(
            status_code=404,
            content={"error": "Frontend no encontrado. Ejecuta el PASO 9 del setup."},
        )
