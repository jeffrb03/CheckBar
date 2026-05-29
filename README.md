# CheckBar 🍸

> **Sistema monolítico de control de inventario y facturación para bar con asistente IA integrado.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-orange)](https://sqlite.org)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-purple)](https://ai.google.dev)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-blueviolet)](#arquitectura)

---

## ¿Qué es CheckBar?

CheckBar digitaliza y automatiza los procesos críticos de un bar:

- **Inventario en tiempo real** — consulta y actualización del stock
- **Registro de ventas** — facturación con descuento automático de inventario
- **Alertas de stock bajo** — notificación visual cuando un producto cae bajo el mínimo
- **Asistente IA (Barman AI)** — chatbot con RAG que responde sobre recetas de cócteles y políticas de inventario
- **Dashboard web moderno** — interfaz glassmorphism dark-mode diseñada en Google Stitch

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
| IA / RAG | Modelos Locales (Ollama / LM Studio) ej. Qwen |
| Frontend | HTML5 + CSS3 + JS Vanilla (diseño de Google Stitch) |
| Tests | pytest (TDD) + Gherkin (BDD) |
| Arquitectura | Hexagonal Monolito |

---

## Estructura del Proyecto

```
CheckBar/
├── .gitignore
├── requirements.txt
├── README.md
├── docs/
│   └── SDD.md                    ← System Design Document con diagramas UML
├── src/
│   ├── main.py                   ← FastAPI app (endpoints + static files)
│   ├── domain/
│   │   ├── producto.py           ← Entidad Producto (lógica de negocio)
│   │   ├── venta.py              ← Entidades Venta + LineaVenta
│   │   ├── inventario_service.py ← Servicio de dominio
│   │   └── exceptions.py        ← Excepciones de dominio
│   ├── ports/
│   │   ├── producto_repository.py ← Interface IProductoRepository
│   │   └── ai_assistant_port.py  ← Interface IAIAssistant
│   └── adapters/
│       ├── database.py           ← SQLite + SQLAlchemy
│       ├── ai_assistant.py       ← Gemini RAG adapter
│       ├── seed.py               ← Seeder con 49 productos de bar
│       ├── recetas_y_reglas.txt  ← Base de conocimiento RAG
│       └── static/
│           ├── index.html        ← Dashboard web
│           ├── style.css         ← Estilos glassmorphism
│           └── app.js            ← Lógica frontend (conexión API)
└── tests/
    ├── bdd/
    │   └── inventario.feature    ← Escenarios Gherkin (BDD)
    └── tdd/
        ├── test_inventario.py    ← 28 pruebas unitarias (TDD)
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

Crea un archivo `.env` en la raíz del proyecto:

```env
# API URL de tu modelo local (ej. Ollama o LM Studio)
LOCAL_AI_URL=http://localhost:11434
LOCAL_AI_MODEL=qwen2.5:7b

# Base de datos (opcional, por defecto usa SQLite local)
DATABASE_URL=sqlite:///./checkbar.db
```

> **⚠️ Importante:** El archivo `.env` está en el `.gitignore` y nunca debe subirse al repositorio.

---

## Ejecución

### 5. Ejecutar el Seeder (poblar la base de datos)

```bash
python src/adapters/seed.py
```

Esto insertará **49 productos realistas** de bar (whiskys, vodkas, rones, ginebras, cervezas, mezcladores, etc.) en la base de datos SQLite.

Salida esperada:
```
[CheckBar] Iniciando seeder de base de datos...
[OK] Seeder completado:
   Productos insertados: 49
   Productos omitidos (ya existian): 0
   Total en catalogo: 49
```

### 6. Levantar el servidor

```bash
# Desde la raíz del proyecto
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

El sistema estará disponible en:

| URL | Descripción |
|---|---|
| `http://localhost:8000` | Dashboard web (frontend) |
| `http://localhost:8000/api/docs` | Documentación Swagger UI |
| `http://localhost:8000/api/redoc` | Documentación ReDoc |
| `http://localhost:8000/productos` | API: Lista de productos |

---

## API Endpoints

### `GET /productos`

Lista todos los productos del inventario con estado de stock.

```bash
curl http://localhost:8000/productos
```

Respuesta:
```json
[
  {
    "id": 1,
    "nombre": "Vodka Absolut Original",
    "categoria": "Vodka",
    "precio_unitario": 75.0,
    "precio_costo": 42.0,
    "stock_actual": 36,
    "stock_minimo": 8,
    "unidad_medida": "Botella 750ml",
    "proveedor": "Distribuidora Norte",
    "tiene_stock_bajo": false,
    "margen_ganancia": 44.0
  }
]
```

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

Pregunta al asistente Barman AI (RAG con Gemini).

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "Como preparo un Mojito?"}'
```

---

## Ejecutar los Tests

### Tests unitarios (TDD)

```bash
python -m pytest tests/tdd/ -v
```

Resultado esperado: **28 tests pasando** ✅

### Tests BDD

Los escenarios Gherkin están en `tests/bdd/inventario.feature`.

```bash
# Requiere pytest-bdd instalado
python -m pytest tests/bdd/ -v
```

---

## Metodologías Aplicadas

### TDD (Test Driven Development)

1. **Red:** Se escribieron 28 pruebas unitarias antes del código del dominio
2. **Green:** Se implementó el código mínimo para hacer pasar todas las pruebas
3. **Refactor:** Se limpió el código manteniendo las pruebas en verde

### BDD (Behavior Driven Development)

Los escenarios en Gherkin (`inventario.feature`) describen el comportamiento del sistema en lenguaje natural:
- Registrar un nuevo producto
- Reducir inventario al vender
- Alertas de stock insuficiente

### SDD (System Design Document)

Ver [docs/SDD.md](./docs/SDD.md) para:
- Arquitectura Hexagonal detallada
- Diagrama de Casos de Uso (Mermaid)
- Diagrama Entidad-Relación (Mermaid)
- Implementación RAG documentada

---

## Asistente IA - Barman AI (RAG)

El asistente usa el patrón **Retrieval-Augmented Generation**:

1. **Retrieval:** Lee `src/adapters/recetas_y_reglas.txt` (5 recetas + 3 políticas)
2. **Augmentation:** Inyecta el contexto en el prompt
3. **Generation:** Llama a tu modelo local (Ollama/LM Studio) para generar la respuesta

El archivo `recetas_y_reglas.txt` contiene:
- Receta de Mojito Clásico
- Receta de Margarita Clásica
- Receta de Old Fashioned
- Receta de Daiquiri de Fresa
- Receta de Aperol Spritz
- Política de Control de Stock Mínimo
- Política de Rotación FIFO
- Política de Mermas y Ajustes

---

## Licencia

MIT License - ver [LICENSE](./LICENSE) para detalles.

---

*Desarrollado con Arquitectura Hexagonal, TDD/BDD y asistencia de IA generativa.*
