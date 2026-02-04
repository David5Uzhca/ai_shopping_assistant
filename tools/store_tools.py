
from typing import Optional
from langchain_core.tools import tool
try:
    from data.supermarket_data import SUPERMARKET_INFO, PRODUCT_LOCATIONS
except ImportError:
    from agent_lm.data.supermarket_data import SUPERMARKET_INFO, PRODUCT_LOCATIONS

@tool
def get_supermarket_hour(day: str = "monday") -> str:
    day = day.lower()
    if "sabado" in day or "saturday" in day:
        key = "saturday"
    elif "domingo" in day or "sunday" in day:
        key = "sunday"
    else:
        key = "monday_friday"
        
    hours = SUPERMARKET_INFO["hours"].get(key, "Horario no disponible")
    return f"El {SUPERMARKET_INFO['name']} abre: {hours} ({key})"

@tool
def get_product_location(product_name: str) -> str:
    product_name = product_name.lower()
    # Búsqueda simple por coincidencia de texto
    for key, location in PRODUCT_LOCATIONS.items():
        if key in product_name or product_name in key:
            return f"El producto '{key}' se encuentra en: {location}"
            
    return f"No encontré información sobre la ubicación de '{product_name}'. Por favor consulta con un empleado."

@tool
def get_supermarket_details() -> str:
    info = SUPERMARKET_INFO
    return f"""
    Nombre: {info['name']}
    Dirección: {info['location']}
    Teléfono: {info['contact']['phone']}
    Servicios: {', '.join(info['services'])}
    """
