
"""
Datos estáticos del Supermercado para el agente RAG/ReAct.
"""

SUPERMARKET_INFO = {
    "name": "Supermercado El Ahorro",
    "location": "Av. Principal 123, Ciudad Central",
    "hours": {
        "monday_friday": "07:00 - 20:30",
        "saturday": "08:00 - 21:00",
        "sunday": "09:00 - 18:00"
    },
    "contact": {
        "phone": "+1 234 567 890",
        "email": "contacto@superahorro.com"
    },
    "services": [
        "Cajero Automático",
        "Farmacia",
        "Panadería",
        "Entrega a Domicilio"
    ]
}

# Base de datos simulada de ubicaciones de productos
PRODUCT_LOCATIONS = {
    "leche": "Pasillo 4, Sección Lácteos",
    "queso": "Pasillo 4, Sección Lácteos",
    "yogurt": "Pasillo 4, Sección Lácteos",
    "pan": "Pasillo 1, Panadería",
    "jabon": "Pasillo 3, Limpieza Personal",
    "shampoo": "Pasillo 3, Limpieza Personal",
    "detergente": "Pasillo 2, Limpieza Hogar",
    "arroz": "Pasillo 5, Granos",
    "frijol": "Pasillo 5, Granos",
    "carne": "Fondo del local, Área de Carnicería",
    "pollo": "Fondo del local, Área de Carnicería",
    "manzana": "Entrada, Sección Frutas y Verduras",
    "banana": "Entrada, Sección Frutas y Verduras",
    "cereal": "Pasillo 6, Desayunos",
    "galletas": "Pasillo 6, Snacks",
    "refresco": "Pasillo 7, Bebidas",
    "agua": "Pasillo 7, Bebidas"
}
