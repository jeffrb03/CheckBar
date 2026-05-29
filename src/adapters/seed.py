"""
Seeder de Base de Datos - CheckBar
Inserta 50 registros realistas de inventario de bar.

Uso:
    python -m src.adapters.seed
    
O directamente:
    python src/adapters/seed.py
"""

import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.adapters.database import create_tables, SessionLocal, ProductoModel


PRODUCTOS_INICIALES = [
    # ──────────────────────────────────────────────────────
    # LICORES PREMIUM (Whiskys)
    # ──────────────────────────────────────────────────────
    {
        "nombre": "Whisky Jack Daniel's Tennessee",
        "categoria": "Whisky",
        "precio_unitario": 95.00,
        "precio_costo": 55.00,
        "stock_actual": 24,
        "stock_minimo": 6,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    {
        "nombre": "Whisky Johnnie Walker Black Label",
        "categoria": "Whisky",
        "precio_unitario": 125.00,
        "precio_costo": 72.00,
        "stock_actual": 18,
        "stock_minimo": 4,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    {
        "nombre": "Whisky Chivas Regal 12 Años",
        "categoria": "Whisky",
        "precio_unitario": 145.00,
        "precio_costo": 85.00,
        "stock_actual": 12,
        "stock_minimo": 3,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    {
        "nombre": "Whisky Glenfiddich 15 Años",
        "categoria": "Whisky Single Malt",
        "precio_unitario": 320.00,
        "precio_costo": 195.00,
        "stock_actual": 6,
        "stock_minimo": 2,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    {
        "nombre": "Whisky Jameson Irish",
        "categoria": "Whisky Irlandés",
        "precio_unitario": 85.00,
        "precio_costo": 48.00,
        "stock_actual": 20,
        "stock_minimo": 5,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Distribuidora Atlántico",
    },
    # ──────────────────────────────────────────────────────
    # VODKAS
    # ──────────────────────────────────────────────────────
    {
        "nombre": "Vodka Absolut Original",
        "categoria": "Vodka",
        "precio_unitario": 75.00,
        "precio_costo": 42.00,
        "stock_actual": 36,
        "stock_minimo": 8,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Distribuidora Norte",
    },
    {
        "nombre": "Vodka Grey Goose",
        "categoria": "Vodka Premium",
        "precio_unitario": 185.00,
        "precio_costo": 110.00,
        "stock_actual": 10,
        "stock_minimo": 3,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    {
        "nombre": "Vodka Belvedere",
        "categoria": "Vodka Premium",
        "precio_unitario": 195.00,
        "precio_costo": 118.00,
        "stock_actual": 8,
        "stock_minimo": 2,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    {
        "nombre": "Vodka Smirnoff",
        "categoria": "Vodka",
        "precio_unitario": 55.00,
        "precio_costo": 28.00,
        "stock_actual": 48,
        "stock_minimo": 12,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Distribuidora Norte",
    },
    {
        "nombre": "Vodka Ciroc Coconut",
        "categoria": "Vodka Saborizado",
        "precio_unitario": 145.00,
        "precio_costo": 85.00,
        "stock_actual": 6,
        "stock_minimo": 2,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    # ──────────────────────────────────────────────────────
    # RONES
    # ──────────────────────────────────────────────────────
    {
        "nombre": "Ron Bacardí Superior",
        "categoria": "Ron",
        "precio_unitario": 62.00,
        "precio_costo": 35.00,
        "stock_actual": 30,
        "stock_minimo": 8,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Distribuidora Caribe",
    },
    {
        "nombre": "Ron Havana Club 7 Años",
        "categoria": "Ron Añejo",
        "precio_unitario": 115.00,
        "precio_costo": 68.00,
        "stock_actual": 15,
        "stock_minimo": 4,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    {
        "nombre": "Ron Diplomatico Reserva",
        "categoria": "Ron Premium",
        "precio_unitario": 175.00,
        "precio_costo": 105.00,
        "stock_actual": 8,
        "stock_minimo": 2,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    {
        "nombre": "Ron Zacapa 23",
        "categoria": "Ron Premium",
        "precio_unitario": 245.00,
        "precio_costo": 148.00,
        "stock_actual": 4,
        "stock_minimo": 2,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    # ──────────────────────────────────────────────────────
    # GINEBRAS
    # ──────────────────────────────────────────────────────
    {
        "nombre": "Gin Hendricks",
        "categoria": "Gin Premium",
        "precio_unitario": 135.00,
        "precio_costo": 78.00,
        "stock_actual": 16,
        "stock_minimo": 4,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora UK Ltd",
    },
    {
        "nombre": "Gin Tanqueray",
        "categoria": "Gin",
        "precio_unitario": 88.00,
        "precio_costo": 50.00,
        "stock_actual": 20,
        "stock_minimo": 5,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora UK Ltd",
    },
    {
        "nombre": "Gin Bombay Sapphire",
        "categoria": "Gin",
        "precio_unitario": 95.00,
        "precio_costo": 55.00,
        "stock_actual": 18,
        "stock_minimo": 4,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora UK Ltd",
    },
    {
        "nombre": "Gin Monkey 47",
        "categoria": "Gin Premium",
        "precio_unitario": 285.00,
        "precio_costo": 175.00,
        "stock_actual": 4,
        "stock_minimo": 2,
        "unidad_medida": "Botella 500ml",
        "proveedor": "Importadora Premium SA",
    },
    # ──────────────────────────────────────────────────────
    # TEQUILAS Y MEZCALES
    # ──────────────────────────────────────────────────────
    {
        "nombre": "Tequila José Cuervo Silver",
        "categoria": "Tequila",
        "precio_unitario": 65.00,
        "precio_costo": 36.00,
        "stock_actual": 24,
        "stock_minimo": 6,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Distribuidora México",
    },
    {
        "nombre": "Tequila Patrón Silver",
        "categoria": "Tequila Premium",
        "precio_unitario": 185.00,
        "precio_costo": 110.00,
        "stock_actual": 10,
        "stock_minimo": 3,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    {
        "nombre": "Tequila Don Julio 1942",
        "categoria": "Tequila Premium",
        "precio_unitario": 450.00,
        "precio_costo": 285.00,
        "stock_actual": 3,
        "stock_minimo": 2,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Premium SA",
    },
    {
        "nombre": "Mezcal Del Maguey",
        "categoria": "Mezcal",
        "precio_unitario": 220.00,
        "precio_costo": 132.00,
        "stock_actual": 6,
        "stock_minimo": 2,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Distribuidora México",
    },
    # ──────────────────────────────────────────────────────
    # LICORES Y CREMAS
    # ──────────────────────────────────────────────────────
    {
        "nombre": "Amaretto Disaronno",
        "categoria": "Licor",
        "precio_unitario": 78.00,
        "precio_costo": 45.00,
        "stock_actual": 12,
        "stock_minimo": 3,
        "unidad_medida": "Botella 700ml",
        "proveedor": "Importadora Italia",
    },
    {
        "nombre": "Triple Sec Cointreau",
        "categoria": "Licor",
        "precio_unitario": 95.00,
        "precio_costo": 58.00,
        "stock_actual": 10,
        "stock_minimo": 3,
        "unidad_medida": "Botella 700ml",
        "proveedor": "Importadora Francia",
    },
    {
        "nombre": "Kahlúa Licor de Café",
        "categoria": "Licor",
        "precio_unitario": 82.00,
        "precio_costo": 48.00,
        "stock_actual": 8,
        "stock_minimo": 2,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Distribuidora México",
    },
    {
        "nombre": "Bailey's Irish Cream",
        "categoria": "Crema",
        "precio_unitario": 75.00,
        "precio_costo": 42.00,
        "stock_actual": 12,
        "stock_minimo": 3,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Distribuidora Atlántico",
    },
    {
        "nombre": "Aperol",
        "categoria": "Aperitivo",
        "precio_unitario": 88.00,
        "precio_costo": 50.00,
        "stock_actual": 15,
        "stock_minimo": 4,
        "unidad_medida": "Botella 700ml",
        "proveedor": "Importadora Italia",
    },
    {
        "nombre": "Campari",
        "categoria": "Aperitivo",
        "precio_unitario": 92.00,
        "precio_costo": 54.00,
        "stock_actual": 10,
        "stock_minimo": 3,
        "unidad_medida": "Botella 700ml",
        "proveedor": "Importadora Italia",
    },
    # ──────────────────────────────────────────────────────
    # VINOS Y ESPUMOSOS
    # ──────────────────────────────────────────────────────
    {
        "nombre": "Champagne Moët & Chandon Imperial",
        "categoria": "Champagne",
        "precio_unitario": 380.00,
        "precio_costo": 235.00,
        "stock_actual": 6,
        "stock_minimo": 3,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Francia",
    },
    {
        "nombre": "Prosecco Mionetto",
        "categoria": "Espumoso",
        "precio_unitario": 95.00,
        "precio_costo": 55.00,
        "stock_actual": 24,
        "stock_minimo": 6,
        "unidad_medida": "Botella 750ml",
        "proveedor": "Importadora Italia",
    },
    # ──────────────────────────────────────────────────────
    # MEZCLADORES Y SODAS
    # ──────────────────────────────────────────────────────
    {
        "nombre": "Agua Tónica Fever-Tree Premium",
        "categoria": "Mezclador",
        "precio_unitario": 12.00,
        "precio_costo": 6.50,
        "stock_actual": 120,
        "stock_minimo": 24,
        "unidad_medida": "Lata 200ml",
        "proveedor": "Distribuidora Bebidas SA",
    },
    {
        "nombre": "Agua Tónica Schweppes",
        "categoria": "Mezclador",
        "precio_unitario": 8.00,
        "precio_costo": 3.50,
        "stock_actual": 200,
        "stock_minimo": 48,
        "unidad_medida": "Lata 355ml",
        "proveedor": "Distribuidora Bebidas SA",
    },
    {
        "nombre": "Jugo de Limón Fresco",
        "categoria": "Mezclador",
        "precio_unitario": 15.00,
        "precio_costo": 8.00,
        "stock_actual": 20,
        "stock_minimo": 5,
        "unidad_medida": "Litro",
        "proveedor": "Mercado Local",
    },
    {
        "nombre": "Jugo de Naranja Natural",
        "categoria": "Mezclador",
        "precio_unitario": 15.00,
        "precio_costo": 8.00,
        "stock_actual": 15,
        "stock_minimo": 5,
        "unidad_medida": "Litro",
        "proveedor": "Mercado Local",
    },
    {
        "nombre": "Jarabe de Azúcar Simple",
        "categoria": "Mezclador",
        "precio_unitario": 10.00,
        "precio_costo": 4.00,
        "stock_actual": 10,
        "stock_minimo": 3,
        "unidad_medida": "Litro",
        "proveedor": "Producción Propia",
    },
    {
        "nombre": "Ginger Beer Bundaberg",
        "categoria": "Mezclador",
        "precio_unitario": 14.00,
        "precio_costo": 7.50,
        "stock_actual": 80,
        "stock_minimo": 24,
        "unidad_medida": "Botella 375ml",
        "proveedor": "Distribuidora Bebidas SA",
    },
    {
        "nombre": "Agua Mineral Perrier",
        "categoria": "Agua",
        "precio_unitario": 12.00,
        "precio_costo": 6.00,
        "stock_actual": 60,
        "stock_minimo": 12,
        "unidad_medida": "Botella 330ml",
        "proveedor": "Distribuidora Bebidas SA",
    },
    {
        "nombre": "Coca-Cola",
        "categoria": "Refresco",
        "precio_unitario": 8.00,
        "precio_costo": 3.00,
        "stock_actual": 144,
        "stock_minimo": 36,
        "unidad_medida": "Lata 355ml",
        "proveedor": "Distribuidora Bebidas SA",
    },
    {
        "nombre": "Red Bull Energy Drink",
        "categoria": "Energizante",
        "precio_unitario": 18.00,
        "precio_costo": 10.00,
        "stock_actual": 72,
        "stock_minimo": 24,
        "unidad_medida": "Lata 250ml",
        "proveedor": "Distribuidora Bebidas SA",
    },
    # ──────────────────────────────────────────────────────
    # CERVEZAS
    # ──────────────────────────────────────────────────────
    {
        "nombre": "Cerveza Corona Extra",
        "categoria": "Cerveza",
        "precio_unitario": 25.00,
        "precio_costo": 12.00,
        "stock_actual": 96,
        "stock_minimo": 24,
        "unidad_medida": "Botella 355ml",
        "proveedor": "Cervecería Nacional",
    },
    {
        "nombre": "Cerveza Heineken",
        "categoria": "Cerveza",
        "precio_unitario": 28.00,
        "precio_costo": 14.00,
        "stock_actual": 72,
        "stock_minimo": 24,
        "unidad_medida": "Botella 330ml",
        "proveedor": "Importadora Holanda",
    },
    {
        "nombre": "Cerveza Modelo Especial",
        "categoria": "Cerveza",
        "precio_unitario": 22.00,
        "precio_costo": 10.00,
        "stock_actual": 120,
        "stock_minimo": 36,
        "unidad_medida": "Botella 355ml",
        "proveedor": "Cervecería Nacional",
    },
    # ──────────────────────────────────────────────────────
    # GARNISH Y COMPLEMENTOS
    # ──────────────────────────────────────────────────────
    {
        "nombre": "Menta Fresca",
        "categoria": "Garnish",
        "precio_unitario": 5.00,
        "precio_costo": 2.00,
        "stock_actual": 15,
        "stock_minimo": 5,
        "unidad_medida": "Manojo",
        "proveedor": "Mercado Local",
    },
    {
        "nombre": "Aceitunas Verdes",
        "categoria": "Garnish",
        "precio_unitario": 8.00,
        "precio_costo": 4.00,
        "stock_actual": 20,
        "stock_minimo": 5,
        "unidad_medida": "Tarro 200g",
        "proveedor": "Distribuidora Alimentos",
    },
    {
        "nombre": "Cerezas Marrasquino",
        "categoria": "Garnish",
        "precio_unitario": 12.00,
        "precio_costo": 6.00,
        "stock_actual": 10,
        "stock_minimo": 3,
        "unidad_medida": "Frasco 400g",
        "proveedor": "Distribuidora Alimentos",
    },
    {
        "nombre": "Sal para Margarita",
        "categoria": "Garnish",
        "precio_unitario": 5.00,
        "precio_costo": 1.50,
        "stock_actual": 8,
        "stock_minimo": 3,
        "unidad_medida": "Kg",
        "proveedor": "Distribuidora Alimentos",
    },
    {
        "nombre": "Limones (bolsa)",
        "categoria": "Fruta",
        "precio_unitario": 15.00,
        "precio_costo": 6.00,
        "stock_actual": 10,
        "stock_minimo": 4,
        "unidad_medida": "Kg",
        "proveedor": "Mercado Local",
    },
    {
        "nombre": "Azúcar Estándar",
        "categoria": "Insumo",
        "precio_unitario": 8.00,
        "precio_costo": 3.00,
        "stock_actual": 12,
        "stock_minimo": 3,
        "unidad_medida": "Kg",
        "proveedor": "Distribuidora Alimentos",
    },
    {
        "nombre": "Hielo en Cubo (bolsa)",
        "categoria": "Insumo",
        "precio_unitario": 15.00,
        "precio_costo": 5.00,
        "stock_actual": 20,
        "stock_minimo": 10,
        "unidad_medida": "Bolsa 5kg",
        "proveedor": "Hielos del Norte",
    },
]


def run_seed():
    """Ejecuta el seeder insertando los 50 productos si no existen."""
    print("[CheckBar] Iniciando seeder de base de datos...")
    
    # Crear tablas si no existen
    create_tables()
    
    db = SessionLocal()
    try:
        insertados = 0
        omitidos = 0
        
        for datos in PRODUCTOS_INICIALES:
            # Verificar si el producto ya existe
            existente = db.query(ProductoModel).filter(
                ProductoModel.nombre == datos["nombre"]
            ).first()
            
            if existente:
                omitidos += 1
                continue
            
            producto = ProductoModel(**datos)
            db.add(producto)
            insertados += 1
        
        db.commit()
        print(f"[OK] Seeder completado:")
        print(f"   Productos insertados: {insertados}")
        print(f"   Productos omitidos (ya existian): {omitidos}")
        print(f"   Total en catalogo: {insertados + omitidos}")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error durante el seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
