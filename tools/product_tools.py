"""
Herramientas para consultar, comparar y procesar compras de productos.
"""
from typing import List, Optional
from db.connection import execute_query, execute_update

def search_products(
    product_name: Optional[str] = None,
    product_sku: Optional[str] = None,
    product_id: Optional[str] = None
) -> str:
    """
    Busca productos en la base de datos por nombre, SKU o ID.
    
    Args:
        product_name: Nombre del producto (búsqueda parcial, case-insensitive)
        product_sku: SKU exacto del producto
        product_id: ID exacto del producto
    
    Returns:
        String con información formateada de los productos encontrados
    """
    conditions = []
    params = []
    
    if product_id:
        conditions.append("product_id = %s")
        params.append(product_id)
    elif product_sku:
        conditions.append("product_sku = %s")
        params.append(product_sku)
    elif product_name:
        conditions.append("LOWER(product_name) LIKE LOWER(%s)")
        params.append(f"%{product_name}%")
    else:
        # Si no hay filtros, retornar todos los productos activos
        conditions.append("is_active = true")
    
    where_clause = " AND ".join(conditions) if conditions else "is_active = true"
    
    query = f"""
        SELECT 
            product_id,
            product_name,
            product_sku,
            supplier_name,
            quantity_on_hand,
            quantity_reserved,
            quantity_available,
            minimum_stock_level,
            reorder_point,
            optimal_stock_level,
            unit_cost,
            total_value,
            warehouse_location,
            stock_status,
            notes
        FROM product_stocks
        WHERE {where_clause}
        ORDER BY product_name
    """
    
    try:
        results = execute_query(query, tuple(params) if params else None)
        
        if not results:
            return f"No se encontraron productos con los criterios especificados."
        
        if len(results) == 1:
            p = results[0]
            return f"""
{p['product_name']}
- ID: {p['product_id']}
- SKU: {p['product_sku']}
- Proveedor: {p['supplier_name']}
- Precio unitario: ${p['unit_cost']:.2f}
- Stock disponible: {p['quantity_available']} unidades (Total: {p['quantity_on_hand']}, Reservadas: {p['quantity_reserved']})
- Ubicación: {p['warehouse_location']}
- Estado: {'Disponible' if p['stock_status'] == 1 else 'No disponible'}
- Valor total en inventario: ${p['total_value']:.2f}
"""
        else:
            # Múltiples resultados
            response = f"Se encontraron {len(results)} productos:\n\n"
            for i, p in enumerate(results, 1):
                response += f"{i}. {p['product_name']} (SKU: {p['product_sku']}) - ${p['unit_cost']:.2f} - Stock: {p['quantity_available']} unidades\n"
            return response
            
    except Exception as e:
        return f"Error al buscar productos: {str(e)}"

def compare_products(product_names: List[str]) -> str:
    """
    Compara múltiples productos mostrando sus características lado a lado.
    
    Args:
        product_names: Lista de nombres de productos a comparar
    
    Returns:
        String con tabla comparativa de los productos
    """
    if not product_names or len(product_names) < 2:
        return "Necesitas proporcionar al menos 2 nombres de productos para comparar."
    
    # Buscar cada producto
    products_data = []
    for name in product_names:
        query = """
            SELECT 
                product_id,
                product_name,
                product_sku,
                supplier_name,
                quantity_on_hand,
                quantity_reserved,
                quantity_available,
                unit_cost,
                total_value,
                warehouse_location,
                stock_status
            FROM product_stocks
            WHERE LOWER(product_name) LIKE LOWER(%s) AND is_active = true
            ORDER BY product_name
            LIMIT 1
        """
        try:
            results = execute_query(query, (f"%{name}%",))
            if results:
                products_data.append(results[0])
        except Exception as e:
            return f"Error al buscar el producto '{name}': {str(e)}"
    
    if not products_data:
        return "No se encontraron productos para comparar."
    
    if len(products_data) < len(product_names):
        found_names = [p['product_name'] for p in products_data]
        return f"Algunos productos no se encontraron. Encontrados: {', '.join(found_names)}"
    
    # Construir tabla comparativa
    response = "COMPARACIÓN DE PRODUCTOS\n\n"
    response += "| Característica | " + " | ".join([p['product_name'] for p in products_data]) + " |\n"
    response += "|" + "---|" * (len(products_data) + 1) + "\n"
    
    # Precio
    prices = [f"${p['unit_cost']:.2f}" for p in products_data]
    response += f"| Precio | {' | '.join(prices)} |\n"
    
    # Stock disponible
    stocks = [str(p['quantity_available']) for p in products_data]
    response += f"| Stock disponible | {' | '.join(stocks)} unidades |\n"
    
    # Stock total
    total_stocks = [str(p['quantity_on_hand']) for p in products_data]
    response += f"| Stock total | {' | '.join(total_stocks)} unidades |\n"
    
    # Proveedor
    suppliers = [p['supplier_name'] for p in products_data]
    response += f"| Proveedor | {' | '.join(suppliers)} |\n"
    
    # Ubicación
    locations = [p['warehouse_location'] for p in products_data]
    response += f"| Ubicación | {' | '.join(locations)} |\n"
    
    # SKU
    skus = [p['product_sku'] for p in products_data]
    response += f"| SKU | {' | '.join(skus)} |\n"
    
    # Estado
    statuses = ["Disponible" if p['stock_status'] == 1 else "No disponible" for p in products_data]
    response += f"| Estado | {' | '.join(statuses)} |\n"
    
    # Análisis adicional
    response += "\nAnálisis:\n"
    cheapest = min(products_data, key=lambda x: x['unit_cost'])
    most_stock = max(products_data, key=lambda x: x['quantity_available'])
    response += f"- Más económico: {cheapest['product_name']} (${cheapest['unit_cost']:.2f})\n"
    response += f"- Mayor disponibilidad: {most_stock['product_name']} ({most_stock['quantity_available']} unidades)\n"
    
    return response

def process_purchase(product_id: str, quantity: int = 1) -> str:
    """
    Procesa una compra: reduce el stock disponible del producto.
    Actualiza quantity_on_hand restando la cantidad comprada.
    
    Args:
        product_id: ID del producto (ej: 'PROD-CEL-03')
        quantity: Cantidad a comprar (default: 1)
    
    Returns:
        String con confirmación de la compra o mensaje de error
    """
    if quantity <= 0:
        return "La cantidad debe ser mayor a 0."
    
    # Primero verificar que el producto existe y tiene stock suficiente
    check_query = """
        SELECT 
            product_name,
            product_sku,
            quantity_on_hand,
            quantity_available,
            unit_cost
        FROM product_stocks
        WHERE product_id = %s AND is_active = true
    """
    
    try:
        product_info = execute_query(check_query, (product_id,))
        
        if not product_info:
            return f"Error: No se encontró el producto con ID '{product_id}' o no está activo."
        
        product = product_info[0]
        
        if product['quantity_available'] < quantity:
            return f"Error: Stock insuficiente. Solo hay {product['quantity_available']} unidades disponibles de {product['product_name']}."
        
        # Actualizar el stock
        update_query = """
            UPDATE product_stocks
            SET 
                quantity_on_hand = quantity_on_hand - %s,
                quantity_available = quantity_available - %s,
                last_updated_at = NOW()
            WHERE product_id = %s
            RETURNING quantity_on_hand, quantity_available
        """
        
        rows_affected = execute_update(update_query, (quantity, quantity, product_id))
        
        if rows_affected == 0:
            return f"Error: No se pudo actualizar el stock del producto '{product_id}'."
        
        # Obtener el stock actualizado
        updated_info = execute_query(check_query, (product_id,))
        updated_product = updated_info[0]
        
        total_cost = product['unit_cost'] * quantity
        
        return f"""¡Compra completada exitosamente!

Producto: {product['product_name']} (SKU: {product['product_sku']})
Precio unitario: ${product['unit_cost']:.2f}
Cantidad comprada: {quantity} unidad(es)
Total pagado: ${total_cost:.2f}
Stock actualizado: 
   - Antes: {product['quantity_on_hand']} unidades totales, {product['quantity_available']} disponibles
   - Ahora: {updated_product['quantity_on_hand']} unidades totales, {updated_product['quantity_available']} disponibles

Tu pedido ha sido procesado correctamente."""
        
    except Exception as e:
        return f"Error al procesar la compra: {str(e)}"

