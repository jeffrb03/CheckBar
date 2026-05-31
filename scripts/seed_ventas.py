from src.adapters.database import SessionLocal, create_tables, VentaModel, LineaVentaModel, ProductoModel
from datetime import datetime, timedelta
import random

create_tables()
db = SessionLocal()

products = db.query(ProductoModel).all()
prod_map = {p.id: p for p in products}

existing_sales = db.query(VentaModel).count()
print(f"Ventas existentes: {existing_sales}")

combos = [
    [(11, 2), (33, 3), (43, 5)],   # Mojito
    [(19, 2), (33, 2), (46, 1)],   # Margarita
    [(1, 1), (49, 2)],             # Whisky on the rocks
    [(6, 2), (38, 2)],             # Vodka + Coca
    [(40, 4)],                     # Cervezas
    [(41, 3), (38, 3)],            # Heineken + coca
    [(16, 1), (31, 2)],            # Gin Tonic
    [(20, 1), (33, 2)],            # Tequila + limon
    [(39, 3)],                     # Red Bull
    [(29, 2)],                     # Champagne
    [(15, 1), (31, 2), (43, 3)],   # Gin menta
    [(42, 6), (49, 1)],            # Modelo
]

metodos = ['Efectivo', 'Tarjeta', 'Transferencia']
now = datetime.utcnow()
total_ventas_creadas = 0

for dias_atras in range(29, -1, -1):
    fecha_base = now - timedelta(days=dias_atras)
    dia_semana = fecha_base.weekday()
    num_ventas = random.randint(12, 22) if dia_semana >= 4 else random.randint(5, 12)

    for i in range(num_ventas):
        combo = random.choice(combos)
        hora = random.randint(18, 23)
        minuto = random.randint(0, 59)
        fecha_venta = fecha_base.replace(hour=hora, minute=minuto, second=random.randint(0, 59))

        lineas_validas = []
        total_venta = 0.0
        for prod_id, max_cant in combo:
            if prod_id in prod_map:
                p = prod_map[prod_id]
                stock_disp = max(1, p.stock_actual // 2) if p.stock_actual > 2 else 1
                cant = random.randint(1, min(max_cant, stock_disp))
                sub = cant * p.precio_unitario
                lineas_validas.append((prod_id, cant, p.precio_unitario, sub))
                total_venta += sub

        if not lineas_validas:
            continue

        num_id = str(total_ventas_creadas + 1).zfill(4)
        fecha_str = fecha_venta.strftime("%Y%m%d")
        num_fact = "CB-" + fecha_str + "-" + num_id

        venta_model = VentaModel(
            numero_factura=num_fact,
            fecha_venta=fecha_venta,
            total=round(total_venta, 2),
            metodo_pago=random.choice(metodos),
            estado="Completada",
            notas="Venta demo",
        )
        db.add(venta_model)
        db.flush()

        for prod_id, cant, precio, sub in lineas_validas:
            linea = LineaVentaModel(
                venta_id=venta_model.id,
                producto_id=prod_id,
                cantidad=cant,
                precio_unitario=precio,
                subtotal=sub,
            )
            db.add(linea)

        total_ventas_creadas += 1

db.commit()
print(f"Ventas creadas: {total_ventas_creadas}")
db.close()
