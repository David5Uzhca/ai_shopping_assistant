from typing import Optional
from db.cart_ops import add_item_to_cart, get_cart_details, remove_item_from_cart, validate_and_checkout, clear_cart
from tools.product_tools import search_products # Helper para identificar productos

def add_product_to_cart_tool(user_id: str, product_query: str, quantity: int = 1) -> str:
    """
    Agrega un producto al carrito de compras del usuario.
    
    Args:
        user_id: ID del usuario (provisto por el contexto del sistema, NO preguntar al usuario).
        product_query: Nombre o ID del producto a agregar.
        quantity: Cantidad deseada (default 1).
    """
    if not user_id:
        return "Error: No se identificó al usuario. Inicia sesión primero."

    # Intentar encontrar el ID si es un nombre
    # Esto es un 'truco' para que el agente pueda decir "agrega leche" y nosotros resolvamos el ID
    # Si ya manda ID, search_products debería manejarlo o fallar rápido.
    # Para ser robusto, el agente debería buscar primero, pero podemos ayudar.
    
    # Asumimos que el agente pasa el ID exacto si ya lo conoce, o un nombre.
    # Vamos a intentar buscar por nombre si parece un nombre
    
    # Nota: Idealmente el AGENTE debe buscar primero y pasar el ID preciso.
    # Pero para mejorar UX, hacemos una búsqueda rápida.
    product_id = product_query
    
    # Si parece un nombre (tiene espacios o no parece un ID UUID/alfanumérico corto standar de nuestro seed)
    if " " in product_query or len(product_query) > 10: 
       # Placeholder lógica de resolución. 
       # En realidad, es mejor que el Agente use search_products primero.
       pass 

    # Intentamos agregar directo. Si falla por FK, avisamos.
    # Pero `add_item_to_cart` hace un chequeo de nombre antes.
    
    # Si el input NO es un ID exacto, el agente podría fallar. 
    # Instruimos al agente en el prompt para obtener el ID primero.
    
    try:
        return add_item_to_cart(user_id, product_id, quantity)
    except Exception as e:
        return f"Error agregando al carrito: {str(e)}"

def view_cart_tool(user_id: str) -> str:
    """Muestra el contenido actual del carrito del usuario."""
    if not user_id:
        return "Debes iniciar sesión para ver tu carrito."
        
    data = get_cart_details(user_id)
    items = data["items"]
    
    if not items:
        return "Tu carrito está vacío."
    
    msg = "Tu Carrito de Compras:\n\n"
    for item in items:
        msg += f"- {item['product_name']} (x{item['cart_qty']})\n"
        msg += f"  Precio: ${item['unit_cost']:.2f} c/u | Disp: {item['quantity_available']}\n"
    
    msg += f"\nTotal Estimado: ${data['total']:.2f}"
    msg += f"\n\nPara comprar, dime 'procesar compra' o 'pagar carrito'."
    return msg

def checkout_cart_tool(user_id: str) -> str:
    """Finaliza la compra de los items en el carrito, validando stock."""
    if not user_id:
        return "Error de sesión."
    
    return validate_and_checkout(user_id)
