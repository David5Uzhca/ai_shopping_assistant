
"""
Datos estáticos de NovaShop (Tienda de Electrónica) para el agente RAG/ReAct.
"""

SUPERMARKET_INFO = {
    "name": "NovaShop",
    "location": "Centro Comercial Mall del Sol, Local 25, Planta Baja",
    "hours": {
        "monday_friday": "10:00 - 21:00",
        "saturday": "10:00 - 22:00",
        "sunday": "11:00 - 20:00"
    },
    "contact": {
        "phone": "+593 99 123 4567",
        "email": "soporte@novashop.ec"
    },
    "services": [
        "Soporte Técnico Especializado",
        "Instalación de Software",
        "Mantenimiento de Laptops",
        "Garantía Extendida",
        "Crédito Directo",
        "Entrega a Domicilio Express"
    ],
    "return_policy": "Aceptamos devoluciones dentro de los 30 días posteriores a la compra con factura original. El producto debe estar sellado y en perfectas condiciones. Productos abiertos tienen 15 días solo por defectos de fábrica.",
    "warranty_policy": "Todos nuestros productos cuentan con 1 año de garantía del fabricante."
}

# Base de datos simulada de ubicaciones de productos
PRODUCT_LOCATIONS = {
    # Laptops
    "laptop hp": "Mesón Central, Zona HP",
    "laptop dell": "Mesón Central, Zona Dell",
    "laptop macbook": "Isla Apple, Entrada Principal",
    "laptop asus": "Mesón Central, Zona Gaming",
    "laptop lenovo": "Mesón Lateral Izquierdo",
    "macbook air": "Isla Apple",
    "macbook pro": "Isla Apple",

    # Celulares
    "iphone 15": "Isla Apple, Vitrina Principal",
    "iphone 14": "Isla Apple, Vitrina Lateral",
    "iphone": "Isla Apple",
    "samsung galaxy s24": "Stand Samsung, Pasillo Principal",
    "samsung a54": "Stand Samsung, Vitrina Media",
    "samsung": "Stand Samsung",
    "xiaomi redmi": "Stand Xiaomi, Pasillo Derecho",
    "celular": "Pasillo Principal, Stands de Marcas",

    # Accesorios
    "cargador": "Pared Posterior, Accesorios",
    "cable usb": "Pared Posterior, Accesorios",
    "funda iphone": "Góndola 1, Accesorios Móviles",
    "estuche": "Góndola 1, Accesorios Móviles",
    "audifonos": "Góndola 2, Audio",
    "airpods": "Isla Apple, Sección Audio",
    "galaxy buds": "Stand Samsung, Sección Audio",
    "mouse": "Góndola 3, Periféricos",
    "teclado": "Góndola 3, Periféricos",
    
    # Impresoras
    "impresora epson": "Pasillo 4, Zona Impresión",
    "impresora hp": "Pasillo 4, Zona Impresión",
    "tinta": "Pasillo 4, Insumos",
    "papel": "Pasillo 4, Insumos",

    # Gaming
    "ps5": "Zona Gaming, Vitrina Sony",
    "playstation 5": "Zona Gaming, Vitrina Sony",
    "nintendo switch": "Zona Gaming, Vitrina Nintendo",
    "xbox series x": "Zona Gaming, Vitrina Xbox",
    "control ps5": "Zona Gaming, Accesorios Consolas",
    
    # Otros
    "tablet": "Mesón Lateral Derecho",
    "ipad": "Isla Apple, Zona iPads",
    "smartwatch": "Vitrinas Centrales, Wearables",
    "apple watch": "Isla Apple, Wearables"
}
