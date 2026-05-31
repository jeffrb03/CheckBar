# CheckBar 🍸

> **Sistema monolítico de control de inventario, ventas y facturación para bar con asistente IA integrado.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-orange)](https://sqlite.org)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-purple)](https://ai.google.dev)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-blueviolet)](#arquitectura)

---

## ¿Qué es CheckBar?

CheckBar digitaliza y automatiza los procesos críticos de un bar:

- **Inventario en tiempo real** — consulta, actualización y alertas de stock bajo
- **Registro de ventas** — facturación con descuento automático de inventario y generación de PDF
- **Dashboard con gráficas** — historial de ventas diarias (30 días) y top 7 productos más vendidos
- **Alertas de notificaciones** — panel desplegable con productos que requieren reposición
- **Barman AI** — asistente inteligente con acceso al inventario real, memoria de conversación y recetas de cócteles

---

## Arquitectura

```
Arquitectura Hexagonal (Ports & Adapters)

┌─────────────────────────────────────────────────────┐
│                   ADAPTADORES                        │
│  FastAPI (HTTP) │ SQLite (DB) │ Gemini API (IA)     │
├─────────────────────────────────────────────────────┤
│                    PUERTOS                           │
│  IProductoRepository │ IAIAssistant                 │
├─────────────────────────────────────────────────────┤
│                    DOMINIO                           │
│  Producto │ Venta │ InventarioService               │
└─────────────────────────────────────────────────────┘
```

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python + FastAPI |
| Base de datos | SQLite + SQLAlchemy ORM |
| IA Principal | Google Gemini 2.0 Flash (API gratuita) |
| IA Fallback | Ollama local (qwen2.5:0.5b) |
| Frontend | HTML5 + CSS3 + JS Vanilla (diseño Google Stitch) |
| Gráficas | Chart.js (línea de ventas + barras top productos) |
| Tests | pytest (TDD) + Gherkin (BDD) |
| Arquitectura | Hexagonal Monolito |

---

## Estructura del Proyecto

```
CheckBar/
├── .gitignore
├── requirements.txt
├── README.md
├── scripts/
│   └── seed_ventas.py            ← Genera 364 ventas de historial (demo)
├── src/
│   ├── main.py                   ← FastAPI app (endpoints + static files)
│   ├── domain/
│   │   ├── producto.py           ← Entidad Producto
│   │   ├── venta.py              ← Entidades Venta + LineaVenta
│   │   ├── inventario_service.py ← Servicio de dominio
│   │   └── exceptions.py        ← Excepciones de dominio
│   ├── ports/
│   │   ├── producto_repository.py ← Interface IProductoRepository
│   │   └── ai_assistant_port.py  ← Interface IAIAssistant
│   └── adapters/
│       ├── database.py           ← SQLite + SQLAlchemy
│       ├── ai_assistant.py       ← Gemini 2.0 Flash (+ fallback Ollama)
│       ├── seed.py               ← Seeder con 50 productos de bar
│       ├── recetas_y_reglas.txt  ← Base de conocimiento (recetas)
│       └── static/
│           ├── index.html        ← Dashboard web
│           ├── style.css         ← Estilos glassmorphism
│           └── app.js            ← Lógica frontend
└── tests/
    ├── bdd/
    │   └── inventario.feature    ← Escenarios Gherkin (BDD)
    └── tdd/
        ├── test_inventario.py    ← Pruebas unitarias (TDD)
        └── fake_repository.py    ← Repositorio en memoria para tests
```

---

## Instalación y Configuración

### Prerrequisitos

- Python 3.10 o superior
- pip
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/jeffrb03/CheckBar.git
cd CheckBar
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto (copia desde `.env.example`):

```env
# --- GEMINI API (principal, gratis en https://aistudio.google.com/apikey) ---
# Pega aquí tu API key. Si está vacía, se usará el modelo local como fallback.
GEMINI_API_KEY=tu_api_key_aqui

# --- MODELO LOCAL (fallback si Gemini falla o no hay API key) ---
LOCAL_AI_URL=http://localhost:11434
LOCAL_AI_MODEL=qwen2.5:0.5b

# Base de datos
DATABASE_URL=sqlite:///./checkbar.db
```

> **⚠️ Importante:** El archivo `.env` está en `.gitignore` y nunca debe subirse al repositorio.

#### Obtener API Key de Gemini (gratuita)

1. Ve a [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Haz clic en **"Create API key"**
3. Pégala en tu `.env` en `GEMINI_API_KEY=`

Si no configuras la key, el sistema usa automáticamente Ollama local como fallback.

---

## Ejecución

### 5. Ejecutar el Seeder de productos

```bash
python src/adapters/seed.py
```

Inserta **50 productos realistas** de bar (whiskys, vodkas, rones, ginebras, cervezas, mezcladores, etc.).

### 5b. (Opcional) Generar historial de ventas de demostración

```bash
python -m scripts.seed_ventas
```

Genera **364 ventas** distribuidas en los últimos 30 días con patrones realistas (más ventas los fines de semana). Útil para poblar las gráficas del dashboard.

### 6. Levantar el servidor

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

El sistema estará disponible en:

| URL | Descripción |
|---|---|
| `http://localhost:8000` | Dashboard web (frontend) |
| `http://localhost:8000/api/docs` | Documentación Swagger UI |
| `http://localhost:8000/api/redoc` | Documentación ReDoc |
| `http://localhost:8000/chat/status` | Estado del backend de IA |

---

## API Endpoints

### `GET /productos`
Lista todos los productos del inventario con estado de stock.

### `POST /productos`
Registra un nuevo producto en el inventario.

### `GET /ventas`
Retorna el historial completo de ventas (usado por las gráficas del dashboard).

### `POST /ventas`
Registra una nueva venta y descuenta el inventario automáticamente.

```bash
curl -X POST http://localhost:8000/ventas \
  -H "Content-Type: application/json" \
  -d '{
    "lineas": [
      {"producto_id": 1, "cantidad": 2, "precio_unitario": 75.0}
    ],
    "metodo_pago": "Efectivo"
  }'
```

### `POST /chat`
Pregunta al asistente Barman AI con acceso al inventario real.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "Que productos tienen stock bajo?"}'
```

### `POST /chat/reset`
Limpia el historial de conversación del asistente.

### `GET /chat/status`
Muestra qué backend de IA está activo (Gemini o local).

---

## Dashboard — Funcionalidades

### KPIs en tiempo real (5 tarjetas)
- Total de productos en inventario
- Productos con stock bajo
- Número de categorías
- Ventas realizadas hoy
- Ingresos de los últimos 7 días

### Gráficas
- **Historial de ventas** (línea suavizada) — ingresos diarios de los últimos 30 días
- **Top 7 productos** (barras horizontales) — productos con mayores ingresos generados

### Notificaciones 🔔
El botón de campanita en la barra superior abre un panel con todos los productos que tienen stock bajo, mostrando stock actual vs. mínimo requerido.

---

## Barman AI — Asistente Inteligente

El asistente usa una estrategia en cascada:

1. **Gemini 2.0 Flash** (si `GEMINI_API_KEY` está configurada) — respuestas en < 2 segundos
2. **Ollama local** (fallback automático) — funciona sin internet

Capacidades:
- **Consulta de inventario real**: responde con datos exactos de la BD (stock actual, precios, alertas)
- **Memoria de conversación**: recuerda el contexto de la sesión
- **Recetas de cócteles**: Mojito, Margarita, Old Fashioned, Daiquiri, Aperol Spritz y más
- **Recomendaciones**: sugiere cócteles según el stock disponible
- **Análisis de ventas**: comenta sobre tendencias y productos más vendidos

El cabezal del chat muestra el backend activo: `✨ Gemini 2.0 Flash` o `Local · modelo`.

---

## Ejecutar los Tests

### Tests unitarios (TDD)

```bash
python -m pytest tests/tdd/ -v
```

### Tests BDD

```bash
python -m pytest tests/bdd/ -v
```

---

## Metodologías Aplicadas

### TDD (Test Driven Development)
1. **Red:** Pruebas unitarias escritas antes del código de dominio
2. **Green:** Implementación mínima para pasar las pruebas
3. **Refactor:** Limpieza manteniendo pruebas en verde

### BDD (Behavior Driven Development)
Escenarios en Gherkin (`inventario.feature`) que describen el comportamiento en lenguaje natural.

### SDD (System Design Document)
Ver [docs/SDD.md](./docs/SDD.md) para arquitectura detallada, diagramas UML y documentación técnica.

---

## Licencia

MIT License - ver [LICENSE](./LICENSE) para detalles.

---

*Desarrollado con Arquitectura Hexagonal, TDD/BDD, Gemini 2.0 Flash y asistencia de IA generativa.*
