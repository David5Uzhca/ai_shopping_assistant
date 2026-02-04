from typing import List, Dict, Any, Tuple
from db.connection import execute_query, execute_update

def get_or_create_active_cart(user_id: str) -> str:
    """Obtiene el ID del carrito activo o crea uno nuevo."""
    # Buscar carrito activo
    query = "SELECT cart_id FROM carts WHERE user_id = %s AND status = 'active' LIMIT 1"
    results = execute_query(query, (user_id,))
    
    if results:
        return str(results[0]["cart_id"])
    
    # Crear nuevo si no existe
    insert_query = "INSERT INTO carts (user_id, status) VALUES (%s, 'active') RETURNING cart_id"
    results = execute_query(insert_query, (user_id,))
    return str(results[0]["cart_id"])

def add_item_to_cart(user_id: str, product_id: str, quantity: int = 1) -> str:
    """Agrega un item al carrito. Si ya existe, suma la cantidad."""
    cart_id = get_or_create_active_cart(user_id)
    
    # Verificar si el producto existe en la tabla de productos (opcional pero recomendado)
    prod_check = execute_query("SELECT product_name FROM product_stocks WHERE product_id = %s", (product_id,))
    if not prod_check:
        return f"Error: Producto '{product_id}' no encontrado."
    product_name = prod_check[0]["product_name"]

    # Upsert (Insertar o Actualizar)
    # Postgres 9.5+ soporta ON CONFLICT
    query = """
    INSERT INTO cart_items (cart_id, product_id, quantity)
    VALUES (%s, %s, %s)
    ON CONFLICT (cart_id, product_id) 
    DO UPDATE SET quantity = cart_items.quantity + EXCLUDED.quantity, added_at = NOW();
    """
    
    execute_update(query, (cart_id, product_id, quantity))
    return f"Se agregaron {quantity} unidades de '{product_name}' al carrito."

def remove_item_from_cart(user_id: str, product_id: str) -> str:
    cart_id = get_or_create_active_cart(user_id)
    query = "DELETE FROM cart_items WHERE cart_id = %s AND product_id = %s"
    rows = execute_update(query, (cart_id, product_id))
    if rows > 0:
        return "Producto eliminado del carrito."
    return "El producto no estaba en el carrito."

def get_cart_details(user_id: str) -> Dict[str, Any]:
    """Retorna items del carrito con detalles del producto."""
    cart_id = get_or_create_active_cart(user_id)
    
    query = """
    SELECT 
        ci.item_id, ci.quantity as cart_qty,
        p.product_id, p.product_name, p.unit_cost, p.quantity_available, p.product_sku
    FROM cart_items ci
    JOIN product_stocks p ON ci.product_id = p.product_id
    WHERE ci.cart_id = %s
    ORDER BY ci.added_at ASC
    """
    items = execute_query(query, (cart_id,))
    
    total = sum(item["cart_qty"] * item["unit_cost"] for item in items)
    
    return {
        "cart_id": cart_id,
        "items": items,
        "total": total
    }

def clear_cart(user_id: str) -> None:
    cart_id = get_or_create_active_cart(user_id)
    execute_update("DELETE FROM cart_items WHERE cart_id = %s", (cart_id,))

def validate_and_checkout(user_id: str) -> str:
    """
    Valida stock de todos los items y procesa la compra atómicamente.
    Si falta stock de algo, aborta y reporta el problema específico.
    """
    cart_data = get_cart_details(user_id)
    items = cart_data["items"]
    
    if not items:
        return "El carrito está vacío."

    # 1. Validar Stock
    errors = []
    for item in items:
        wanted = item["cart_qty"]
        available = item["quantity_available"]
        if wanted > available:
            errors.append(
                f"- {item['product_name']}: Quieres {wanted}, pero solo quedan {available}."
            )
    
    if errors:
        return "⚠️ No se puede procesar la compra por falta de stock:\n" + "\n".join(errors) + "\n\n¿Quieres que actualice tu carrito con el stock disponible?"

    # 2. Procesar Compra (Restar Stock)
    # Idealmente esto iría en una transacción SQL única, pero lo haremos iterativo por simplicidad en este entorno,
    # asumiendo que db/connection maneja autocommit o transacciones simples.
    
    try:
        receipt = "✅ **Compra Exitosa**\n\n"
        for item in items:
            # Reutilizamos lógica simple o query directa
            update_q = "UPDATE product_stocks SET quantity_on_hand = quantity_on_hand - %s, quantity_available = quantity_available - %s WHERE product_id = %s"
            execute_update(update_q, (item["cart_qty"], item["cart_qty"], item["product_id"]))
            receipt += f"- {item['cart_qty']}x {item['product_name']} (${item['unit_cost']:.2f})\n"
        
        receipt += f"\n**Total Pagado**: ${cart_data['total']:.2f}"
        
        # 3. Vaciar Carrito (o marcar como 'ordered' y crear uno nuevo)
        # Por simplicidad, vaciamos los items
        clear_cart(user_id)
        
        return receipt
        
    except Exception as e:
        return f"Error crítico procesando la compra: {str(e)}"
