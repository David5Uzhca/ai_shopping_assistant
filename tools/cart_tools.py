from typing import Optional
from db.cart_ops import add_item_to_cart, get_cart_details, remove_item_from_cart, validate_and_checkout, clear_cart
from tools.product_tools import search_products # Helper para identificar productos

def add_product_to_cart_tool(user_id: str, product_id: str, quantity: int = 1) -> str:
    """
    Agrega un producto al carrito usando su product_id exacto.
    """
    if not user_id:
        return "Error: No se identificó al usuario. Inicia sesión primero."
    
    try:
        # Validamos que product_id parezca un ID (opcional, pero buena práctica)
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
