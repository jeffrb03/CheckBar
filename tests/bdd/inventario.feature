# language: es
# encoding: utf-8
# ============================================================
# Feature: Gestión de Inventario del Bar (BDD - Gherkin)
# Proyecto: CheckBar
# Metodología: Behavior Driven Development
# ============================================================

Característica: Gestión de Inventario del Bar
  Como bartender o gerente del bar
  Quiero gestionar el inventario de productos
  Para mantener el stock actualizado y evitar quiebres de inventario

  Antecedentes:
    Dado que el sistema CheckBar está operativo
    Y que la base de datos está inicializada

  # ─────────────────────────────────────────────────────────
  # ESCENARIO 1: Registrar un nuevo producto en inventario
  # ─────────────────────────────────────────────────────────
  Escenario: Registrar un nuevo producto exitosamente
    Dado que no existe un producto llamado "Tequila Patrón Silver"
    Cuando el gerente registra un nuevo producto con los siguientes datos:
      | campo           | valor                |
      | nombre          | Tequila Patrón Silver |
      | categoria       | Licor                |
      | precio_unitario | 85.00                |
      | precio_costo    | 45.00                |
      | stock_actual    | 24                   |
      | stock_minimo    | 5                    |
      | unidad_medida   | Botella              |
    Entonces el producto "Tequila Patrón Silver" debe aparecer en el inventario
    Y el stock actual debe ser 24 unidades
    Y el sistema debe confirmar el registro exitoso

  Escenario: Intentar registrar un producto con nombre duplicado
    Dado que existe un producto llamado "Vodka Absolut" con stock 10
    Cuando el gerente intenta registrar otro producto llamado "Vodka Absolut"
    Entonces el sistema debe rechazar el registro
    Y mostrar el mensaje de error "El producto ya existe en el inventario"

  Escenario: Registrar un producto con precio negativo
    Cuando el gerente intenta registrar un producto con precio_unitario de -50
    Entonces el sistema debe rechazar el registro
    Y mostrar el mensaje de error "El precio unitario debe ser mayor a cero"

  # ─────────────────────────────────────────────────────────
  # ESCENARIO 2: Reducción de inventario al registrar venta
  # ─────────────────────────────────────────────────────────
  Escenario: Reducir inventario correctamente al vender
    Dado que existe un producto llamado "Ron Bacardí" con stock 20
    Cuando el bartender registra una venta de 3 unidades de "Ron Bacardí"
    Entonces el stock de "Ron Bacardí" debe ser 17 unidades
    Y la venta debe registrarse con estado "Completada"
    Y debe existir un movimiento de inventario de tipo "salida" por 3 unidades

  Escenario: Reducir inventario de múltiples productos en una sola venta
    Dado que existe un producto llamado "Gin Hendricks" con stock 15
    Y que existe un producto llamado "Agua Tónica Schweppes" con stock 48
    Cuando el bartender registra una venta con:
      | producto                   | cantidad |
      | Gin Hendricks              | 2        |
      | Agua Tónica Schweppes      | 4        |
    Entonces el stock de "Gin Hendricks" debe ser 13 unidades
    Y el stock de "Agua Tónica Schweppes" debe ser 44 unidades
    Y el total de la venta debe calcularse correctamente

  Escenario: Cancelar una venta debe restaurar el inventario
    Dado que existe un producto llamado "Whisky Jack Daniel's" con stock 8
    Y que se ha registrado una venta de 2 unidades de "Whisky Jack Daniel's"
    Cuando el gerente cancela esa venta
    Entonces el stock de "Whisky Jack Daniel's" debe volver a 8 unidades
    Y la venta debe tener estado "Cancelada"

  # ─────────────────────────────────────────────────────────
  # ESCENARIO 3: Alerta de stock insuficiente
  # ─────────────────────────────────────────────────────────
  Escenario: Alerta cuando el stock cae por debajo del mínimo
    Dado que existe un producto llamado "Champagne Moët" con stock 3
    Y que el stock mínimo de "Champagne Moët" es 5
    Cuando el bartender consulta el inventario
    Entonces el sistema debe marcar "Champagne Moët" con alerta de stock bajo
    Y la alerta debe indicar "Stock bajo: 3 unidades (mínimo: 5)"

  Escenario: Venta que lleva el stock justo al mínimo genera alerta
    Dado que existe un producto llamado "Aperol" con stock 8
    Y que el stock mínimo de "Aperol" es 5
    Cuando el bartender registra una venta de 3 unidades de "Aperol"
    Entonces el stock de "Aperol" debe ser 5 unidades
    Y el sistema debe generar una alerta de stock bajo para "Aperol"

  Escenario: Venta que supera el stock disponible debe ser rechazada
    Dado que existe un producto llamado "Vodka Grey Goose" con stock 2
    Cuando el bartender intenta registrar una venta de 5 unidades de "Vodka Grey Goose"
    Entonces el sistema debe rechazar la venta
    Y mostrar el mensaje "Stock insuficiente: solo hay 2 unidades disponibles de Vodka Grey Goose"
    Y el stock de "Vodka Grey Goose" debe permanecer en 2 unidades

  Escenario: Alerta de stock bajo no se genera cuando el stock está por encima del mínimo
    Dado que existe un producto llamado "Tequila José Cuervo" con stock 20
    Y que el stock mínimo de "Tequila José Cuervo" es 5
    Cuando el bartender consulta el inventario
    Entonces el producto "Tequila José Cuervo" no debe tener alerta de stock bajo

  # ─────────────────────────────────────────────────────────
  # ESCENARIO ADICIONAL: Consulta del Asistente IA (RAG)
  # ─────────────────────────────────────────────────────────
  Escenario: El asistente responde una pregunta sobre receta de cóctel
    Dado que el asistente IA está configurado con la base de conocimiento
    Cuando el bartender pregunta "¿Cómo preparo un Mojito?"
    Entonces el asistente debe responder con los ingredientes del Mojito
    Y la respuesta debe mencionar "ron" o "menta" o "lima"
    Y la respuesta no debe estar vacía
