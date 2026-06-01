# CheckBar 🍸

> **Sistema integral de control de inventario, punto de venta y asistencia inteligente por IA para bares y establecimientos de bebidas.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Gemini 2.0 Flash](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-8E24AA?logo=google&logoColor=white)](https://ai.google.dev)
[![Architecture](https://img.shields.io/badge/Arch-Hexagonal-blueviolet)](#-arquitectura)
[![TDD](https://img.shields.io/badge/Tests-TDD%20%2B%20BDD-green)](#-ejecutar-los-tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Características Principales](#-características-principales)
- [Arquitectura](#-arquitectura)
- [Stack Tecnológico](#-stack-tecnológico)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Ejecución](#-ejecución)
- [API Reference](#-api-reference)
- [Dashboard — Funcionalidades UI](#-dashboard--funcionalidades-ui)
- [Barman AI — Asistente Inteligente](#-barman-ai--asistente-inteligente)
- [Tests](#-ejecutar-los-tests)
- [Metodologías Aplicadas](#-metodologías-aplicadas)
- [Documentación Técnica](#-documentación-técnica)
- [Licencia](#-licencia)

---

## 🎯 Descripción General

**CheckBar** es un sistema monolítico construido con Arquitectura Hexagonal (Ports & Adapters) que digitaliza y automatiza las operaciones críticas de un bar: gestión de inventario en tiempo real, punto de venta con descuento automático de stock, visualización analítica mediante gráficas interactivas, y un asistente inteligente potenciado por **Google Gemini 2.0 Flash** con acceso directo a la base de datos.

El sistema fue desarrollado aplicando estrictamente **TDD** (Test-Driven Development) y **BDD** (Behavior-Driven Development) como metodologías de ingeniería de software.

---

## ✨ Características Principales

### 📦 Gestión de Inventario
- CRUD completo de productos con 50+ ítems pre-cargados (whiskys, vodkas, rones, ginebras, tequilas, cervezas, mezcladores, garnishes)
- Detección automática de stock bajo con umbrales configurables por producto
- Cálculo de márgenes de ganancia en tiempo real
- Búsqueda instantánea por nombre de producto

### 💰 Punto de Venta (POS)
- Registro de ventas multi-producto con líneas de detalle
- Descuento automático de inventario al confirmar venta
- Soporte para múltiples métodos de pago (Efectivo, Tarjeta, Transferencia)
- Validación de stock disponible antes de confirmar
- Generación de número de factura automático

### 📊 Dashboard Analítico
- **5 KPIs en tiempo real**: Total productos, Stock bajo, Categorías, Ventas de hoy, Ingresos 7 días
- **Gráfica de línea (Chart.js)**: Historial de ingresos diarios de los últimos 30 días con gradiente y animaciones
- **Gráfica de barras horizontal**: Top 7 productos por ingresos generados con nombres reales
- **Panel de notificaciones 🔔**: Desplegable con lista detallada de productos que necesitan reposición

### 🤖 Barman AI — Asistente Inteligente
- **Gemini 2.0 Flash** como motor principal (API gratuita, respuestas en < 2 segundos)
- **Fallback automático** a Ollama local (`qwen2.5:0.5b`) si Gemini falla o no hay API key
- **Acceso directo al inventario real** de la base de datos en cada consulta
- **Memoria de conversación** persistente durante la sesión (hasta 16 intercambios)
- **Base de conocimiento RAG** con recetas de cócteles y políticas del bar
- **Detección y manejo transparente de rate limits** (HTTP 429) sin interrumpir al usuario

---

## 🏛 Arquitectura

El sistema implementa la **Arquitectura Hexagonal** (Alistair Cockburn, 2005), también conocida como Ports & Adapters. Esta arquitectura garantiza que la lógica de negocio sea completamente independiente de la infraestructura.

```
┌──────────────────────────────────────────────────────────────────┐
│                        ADAPTADORES (I/O)                          │
│                                                                    │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐    │
│   │   FastAPI     │   │   SQLite +   │   │  Gemini 2.0 Flash│    │
│   │   (HTTP API)  │   │  SQLAlchemy  │   │  + Ollama Local  │    │
│   │   Driving     │   │   Driven     │   │  Driven (AI)     │    │
│   └──────┬───────┘   └──────┬───────┘   └────────┬─────────┘    │
│          │                   │                     │               │
│   ┌──────▼───────────────────▼─────────────────────▼───────────┐  │
│   │                     PUERTOS (Interfaces)                    │  │
│   │   IProductoRepository │ IVentaRepository │ IAIAssistant    │  │
│   └────────────────────────────┬───────────────────────────────┘  │
│                                │                                   │
│   ┌────────────────────────────▼──────────────────────────────┐   │
│   │                       DOMINIO (Core)                       │   │
│   │   Producto │ Venta │ LineaVenta │ InventarioService       │   │
│   │   Excepciones: StockInsuficiente, ProductoNoEncontrado    │   │
│   │   ⚠️ CERO dependencias de infraestructura                │   │
│   └────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### Flujo de Datos: Registrar Venta

```
Cliente HTTP  →  POST /ventas (FastAPI Adapter)
                    → InventarioService.registrar_venta()
                        → IProductoRepository.obtener(id)  →  SQLite
                        → Producto.validar_stock()         →  Dominio
                        → IVentaRepository.guardar(venta)  →  SQLite
                    ← HTTP 201 + Factura JSON
```

---

## ⚙️ Stack Tecnológico

| Capa | Tecnología | Propósito |
|---|---|---|
| **Backend** | Python 3.10+ / FastAPI | API REST con auto-documentación OpenAPI |
| **ORM** | SQLAlchemy 2.0 | Mapeo objeto-relacional con tipado |
| **Base de datos** | SQLite | Cero configuración, ideal para despliegue local |
| **IA Principal** | Google Gemini 2.0 Flash | Asistente inteligente (API REST, sin SDK) |
| **IA Fallback** | Ollama (qwen2.5:0.5b) | Operación offline sin internet |
| **Frontend** | HTML5 + CSS3 + JS Vanilla | SPA sin build tools, diseño Google Stitch |
| **Gráficas** | Chart.js 4.x | Visualizaciones interactivas en canvas |
| **HTTP Client** | httpx | Llamadas async a APIs externas |
| **Tests** | pytest + pytest-bdd | TDD unitario + BDD con Gherkin |
| **Arquitectura** | Hexagonal (Monolito) | Testabilidad + separación de concerns |

---

## 📁 Estructura del Proyecto

```
CheckBar/
├── .env                          # Variables de entorno (NUNCA se sube a Git)
├── .env.example                  # Plantilla de variables de entorno
├── .gitignore                    # Exclusiones de Git
├── requirements.txt              # Dependencias Python
├── README.md                     # Este documento
├── checkbar.db                   # Base de datos SQLite (auto-generada)
│
├── docs/
│   └── SDD.md                    # System Design Document (diagramas UML, ER, RAG)
│
├── scripts/
│   └── seed_ventas.py            # Genera 364 ventas históricas de demostración
│
├── src/
│   ├── __init__.py
│   ├── main.py                   # ← Punto de entrada: FastAPI app + todos los endpoints
│   │
│   ├── domain/                   # 🔵 NÚCLEO — Lógica de negocio pura
│   │   ├── __init__.py
│   │   ├── producto.py           #    Entidad Producto + reglas de stock
│   │   ├── venta.py              #    Entidades Venta + LineaVenta
│   │   ├── inventario_service.py #    Servicio de dominio (operaciones CRUD)
│   │   └── exceptions.py         #    Excepciones tipadas del dominio
│   │
│   ├── ports/                    # 🟡 CONTRATOS — Interfaces abstractas
│   │   ├── __init__.py
│   │   ├── producto_repository.py #   ABC: IProductoRepository
│   │   └── ai_assistant_port.py   #   ABC: IAIAssistant
│   │
│   └── adapters/                 # 🟢 IMPLEMENTACIONES — Infraestructura
│       ├── __init__.py
│       ├── database.py           #    SQLite + SQLAlchemy (repositorios concretos)
│       ├── ai_assistant.py       #    Gemini 2.0 Flash + Ollama (cascada con fallback)
│       ├── seed.py               #    Seeder: 50 productos realistas de bar
│       ├── recetas_y_reglas.txt  #    Base de conocimiento RAG (5 recetas + 3 políticas)
│       └── static/               #    Frontend web
│           ├── index.html        #       Dashboard SPA (diseño Google Stitch)
│           ├── style.css         #       Estilos glassmorphism dark-mode
│           └── app.js            #       Lógica frontend (700+ LOC)
│
└── tests/
    ├── __init__.py
    ├── bdd/
    │   ├── __init__.py
    │   └── inventario.feature    # Escenarios Gherkin (BDD)
    └── tdd/
        ├── __init__.py
        ├── test_inventario.py    # 28 pruebas unitarias (TDD)
        └── fake_repository.py   # Repositorio in-memory para testing
```

---

## 🚀 Instalación y Configuración

### Prerrequisitos

| Requisito | Versión | Notas |
|---|---|---|
| Python | 3.10+ | Verificar con `python --version` |
| pip | Cualquiera | Incluido con Python |
| Git | Cualquiera | Para clonar el repositorio |
| Ollama | (Opcional) | Solo si no configuras Gemini API |

### 1. Clonar el repositorio

```bash
git clone https://github.com/jeffrb03/CheckBar.git
cd CheckBar
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv

# Windows (PowerShell)
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar la plantilla
cp .env.example .env
```

Editar `.env` con tus valores:

```env
# ── ASISTENTE IA (elige una opción) ──────────────────────────

# OPCIÓN A: Gemini 2.0 Flash (RECOMENDADO — gratis, rápido, inteligente)
# Obtén tu key en: https://aistudio.google.com/apikey
GEMINI_API_KEY=tu_api_key_aqui

# OPCIÓN B: Modelo local con Ollama (fallback automático si Gemini falla)
LOCAL_AI_URL=http://localhost:11434
LOCAL_AI_MODEL=qwen2.5:0.5b

# ── BASE DE DATOS ────────────────────────────────────────────
DATABASE_URL=sqlite:///./checkbar.db
```

> **⚠️ Seguridad:** El archivo `.env` está en `.gitignore`. Nunca expongas tu API key en el repositorio.

---

## ▶️ Ejecución

### 5. Poblar la base de datos (primera vez)

```bash
# Insertar 50 productos realistas de bar
python src/adapters/seed.py

# (Opcional) Generar 364 ventas de historial para demo
python -m scripts.seed_ventas
```

### 6. Levantar el servidor

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### URLs disponibles

| URL | Descripción |
|---|---|
| [`http://localhost:8000`](http://localhost:8000) | 🖥️ Dashboard web (frontend completo) |
| [`http://localhost:8000/api/docs`](http://localhost:8000/api/docs) | 📖 Swagger UI (documentación interactiva) |
| [`http://localhost:8000/api/redoc`](http://localhost:8000/api/redoc) | 📖 ReDoc (documentación alternativa) |
| [`http://localhost:8000/chat/status`](http://localhost:8000/chat/status) | 🤖 Estado del backend de IA activo |

---

## 📡 API Reference

### Inventario

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/productos` | Lista todos los productos con estado de stock |
| `POST` | `/productos` | Registra un nuevo producto |

### Ventas

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/ventas` | Historial completo de ventas (alimenta las gráficas) |
| `POST` | `/ventas` | Registra venta con descuento automático de inventario |

### Asistente IA

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/chat` | Envía pregunta al Barman AI |
| `POST` | `/chat/reset` | Limpia historial de conversación |
| `GET` | `/chat/status` | Muestra backend activo (Gemini/Local) |

### Sistema

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/health` | Health check del servidor |

### Ejemplo: Registrar una venta

```bash
curl -X POST http://localhost:8000/ventas \
  -H "Content-Type: application/json" \
  -d '{
    "lineas": [
      {"producto_id": 1, "cantidad": 2, "precio_unitario": 75.0},
      {"producto_id": 5, "cantidad": 1, "precio_unitario": 45.0}
    ],
    "metodo_pago": "Tarjeta"
  }'
```

### Ejemplo: Preguntar al asistente

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Qué productos tienen stock bajo?"}'
```

---

## 🖥️ Dashboard — Funcionalidades UI

### KPIs en Tiempo Real (5 tarjetas)

| KPI | Fuente | Actualización |
|---|---|---|
| Total Productos | `GET /productos` | Al cargar / refrescar |
| Stock Bajo | Filtro `tiene_stock_bajo == true` | Al cargar / refrescar |
| Categorías | `Set` único de categorías | Al cargar / refrescar |
| Ventas Hoy | `GET /ventas` filtrado por fecha local | Al cargar / refrescar |
| Ingresos 7 Días | Suma de `total` últimos 7 días | Al cargar / refrescar |

### Gráficas Interactivas (Chart.js)

- **Historial de Ventas** (2/3 del ancho) — Gráfica de línea suavizada con gradiente morado, mostrando ingresos diarios de los últimos 30 días
- **Top 7 Productos** (1/3 del ancho) — Barras horizontales con colores únicos, mostrando nombres reales de productos y sus ingresos generados

### Panel de Notificaciones 🔔

Al hacer clic en el ícono de campanita de la barra superior:
- Se despliega un panel flotante con glassmorphism
- Lista todos los productos con stock bajo (nombre, categoría, stock actual vs. mínimo)
- Badge numérico sobre el ícono indica la cantidad de alertas
- Se cierra al hacer clic fuera del panel

---

## 🤖 Barman AI — Asistente Inteligente

### Estrategia de IA en Cascada

```
Pregunta del usuario
        │
        ▼
┌─ GEMINI 2.0 FLASH ─┐     (si GEMINI_API_KEY configurada)
│  • API REST directa │     • Respuesta en < 2 segundos
│  • Temperatura: 0.3  │     • Contexto de inventario real
│  • Max tokens: 400   │     • Memoria de conversación
└─────────┬───────────┘
          │ si HTTP 429 (rate limit) o sin API key
          ▼
┌─ OLLAMA LOCAL ──────┐     (fallback silencioso y automático)
│  • qwen2.5:0.5b     │     • Funciona sin internet
│  • Temperatura: 0.1  │     • Contexto inyectado en mensaje del usuario
│  • Max tokens: 300   │     • Optimizado para modelos ultra-pequeños
└─────────────────────┘
```

### Capacidades del Asistente

| Capacidad | Descripción |
|---|---|
| **Consulta de inventario** | Lee datos reales de la BD (stock actual, precios, alertas) |
| **Memoria conversacional** | Recuerda contexto de la sesión (hasta 16 turnos Gemini / 6 Ollama) |
| **Recetas de cócteles** | Mojito, Margarita, Old Fashioned, Daiquiri, Aperol Spritz |
| **Recomendaciones** | Sugiere cócteles según disponibilidad real de ingredientes |
| **Detección de stock bajo** | Identifica y alerta sobre productos bajo el umbral mínimo |
| **Tolerancia a fallos** | Rate limits de Gemini se manejan transparentemente |

### Patrón RAG (Retrieval-Augmented Generation)

```
1. RETRIEVAL      →  Inventario real (SQLite) + Recetas (recetas_y_reglas.txt)
2. AUGMENTATION   →  Se inyecta como contexto en el System Prompt
3. GENERATION     →  Gemini/Ollama genera respuesta contextualizada
```

---

## 🧪 Ejecutar los Tests

### Tests Unitarios (TDD)

```bash
python -m pytest tests/tdd/ -v
```

**28 pruebas unitarias** cubriendo:
- Creación y validación de entidades `Producto` y `Venta`
- Operaciones CRUD del `InventarioService`
- Validaciones de negocio (stock insuficiente, precio inválido, cantidad inválida)
- Cálculo de márgenes de ganancia
- Detección de stock bajo
- Descuento automático de inventario al vender

### Tests BDD (Gherkin)

```bash
python -m pytest tests/bdd/ -v
```

Escenarios en lenguaje natural (`inventario.feature`):
- ✅ Registrar un nuevo producto en el inventario
- ✅ Reducir inventario al realizar una venta
- ✅ Recibir alerta cuando el stock cae bajo el mínimo

---

## 📐 Metodologías Aplicadas

### TDD (Test-Driven Development)

```
🔴 RED      → Se escribieron 28 pruebas unitarias ANTES del código de dominio
🟢 GREEN    → Se implementó el código mínimo para pasar todas las pruebas
🔵 REFACTOR → Se limpió y optimizó el código manteniendo las pruebas en verde
```

Todas las pruebas usan un `FakeRepository` (repositorio in-memory) que implementa la misma interfaz `IProductoRepository`, demostrando la inversión de dependencias de la Arquitectura Hexagonal.

### BDD (Behavior-Driven Development)

Escenarios escritos en **Gherkin** que describen el comportamiento esperado del sistema desde la perspectiva del usuario, ejecutables con `pytest-bdd`.

### SDD (System Design Document)

Documentación técnica completa en [`docs/SDD.md`](./docs/SDD.md) incluyendo:
- Arquitectura Hexagonal detallada con diagramas ASCII
- Diagrama de Casos de Uso (Mermaid)
- Diagrama Entidad-Relación (Mermaid)
- Arquitectura RAG completa con pipeline documentado
- Tabla de decisiones de diseño con justificaciones

---

## 📚 Documentación Técnica

| Documento | Ubicación | Contenido |
|---|---|---|
| **README.md** | Raíz del proyecto | Este documento — guía completa |
| **SDD.md** | `docs/SDD.md` | System Design Document con diagramas UML y ER |
| **Swagger UI** | `/api/docs` (runtime) | Documentación interactiva de la API |
| **ReDoc** | `/api/redoc` (runtime) | Documentación alternativa de la API |
| **Gherkin** | `tests/bdd/inventario.feature` | Especificación BDD en lenguaje natural |

---

## 📄 Licencia

MIT License — ver [LICENSE](./LICENSE) para detalles.

---

<div align="center">

**CheckBar** — Desarrollado con Arquitectura Hexagonal, TDD/BDD, Google Gemini 2.0 Flash y asistencia de IA generativa.

*Sistema de Control de Inventario y Facturación para Bar con Asistente Inteligente*

</div>
