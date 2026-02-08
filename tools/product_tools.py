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
    """    Busca productos en la base de datos por nombre, SKU o ID.    """
    conditions = []
    params = []
    
    if product_id:
        conditions.append("ps.product_id = %s")
        params.append(product_id)
    elif product_sku:
        conditions.append("ps.product_sku = %s")
        params.append(product_sku)
    elif product_name:
        conditions.append("LOWER(ps.product_name) LIKE LOWER(%s)")
        params.append(f"%{product_name}%")
    else:
        # Si no hay filtros, retornar todos los productos activos
        conditions.append("ps.is_active = true")
    
    where_clause = " AND ".join(conditions) if conditions else "ps.is_active = true"
    
    query = f"""
        SELECT 
            ps.product_id,
            ps.product_name,
            ps.product_sku,
            ps.supplier_name,
            ps.quantity_on_hand,
            ps.quantity_reserved,
            ps.quantity_available,
            ps.minimum_stock_level,
            ps.reorder_point,
            ps.optimal_stock_level,
            ps.unit_cost,
            ps.total_value,
            ps.warehouse_location,
            ps.stock_status,
            ps.notes,
            po.discount_percentage,
            po.description as offer_desc
        FROM product_stocks ps
        LEFT JOIN product_offers po ON ps.product_id = po.product_id 
            AND po.is_active = true 
            AND NOW() BETWEEN po.start_date AND po.end_date
        WHERE {where_clause}
        ORDER BY ps.product_id -- Orden deterministico
    """
    
    try:
        results = execute_query(query, tuple(params) if params else None)
        
        if not results:
            return f"No se encontraron productos con los criterios especificados."
        
        if len(results) == 1:
            p = results[0]
            price_str = f"${p['unit_cost']:.2f}"
            
            # Lógica de Oferta
            if p['discount_percentage']:
                discount = float(p['discount_percentage'])
                original_price = float(p['unit_cost'])
                final_price = original_price * (1 - discount / 100)
                price_str = f"${final_price:.2f} (Oferta: {discount}% OFF - Precio Normal: ${original_price:.2f} - {p['offer_desc']})"

            return f"""
{p['product_name']}
- ID: {p['product_id']}
- SKU: {p['product_sku']}
- Proveedor: {p['supplier_name']}
- Precio: {price_str}
- Stock disponible: {p['quantity_available']} unidades (Total: {p['quantity_on_hand']}, Reservadas: {p['quantity_reserved']})
- Ubicación: {p['warehouse_location']}
- Estado: {'Disponible' if p['stock_status'] == 1 else 'No disponible'}
"""
        else:
            # Múltiples resultados
            response = f"Se encontraron {len(results)} productos:\n\n"
            for i, p in enumerate(results, 1):
                price_display = f"${p['unit_cost']:.2f}"
                if p['discount_percentage']:
                    discount = float(p['discount_percentage'])
                    final_price = float(p['unit_cost']) * (1 - discount / 100)
                    price_display = f"${final_price:.2f} (Oferta {discount}%)"
                
                response += f"{i}. {p['product_name']} (SKU: {p['product_sku']}) - {price_display} - Stock: {p['quantity_available']} unidades\n"
            return response
            
    except Exception as e:
        return f"Error al buscar productos: {str(e)}"

def compare_products(product_names: List[str]) -> str:
    """    Compara múltiples productos mostrando sus características lado a lado.    """
    if not product_names or len(product_names) < 2:
        return "Necesitas proporcionar al menos 2 nombres de productos para comparar."
    
    # Buscar cada producto
    products_data = []
    for name in product_names:
        query = """
            SELECT 
                ps.product_id,
                ps.product_name,
                ps.product_sku,
                ps.supplier_name,
                ps.quantity_on_hand,
                ps.quantity_reserved,
                ps.quantity_available,
                ps.unit_cost,
                ps.total_value,
                ps.warehouse_location,
                ps.stock_status,
                po.discount_percentage,
                po.description as offer_desc
            FROM product_stocks ps
            LEFT JOIN product_offers po ON ps.product_id = po.product_id 
                AND po.is_active = true 
                AND NOW() BETWEEN po.start_date AND po.end_date
            WHERE LOWER(ps.product_name) LIKE LOWER(%s) AND ps.is_active = true
            ORDER BY ps.product_name
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
    response = "COMPARACIÓN DE PRODUCTOS (Con Ofertas)\n\n"
    response += "| Característica | " + " | ".join([p['product_name'] for p in products_data]) + " |\n"
    response += "|" + "---|" * (len(products_data) + 1) + "\n"
    
    # Precio
    # Precio
    prices = []
    for p in products_data:
        if p['discount_percentage']:
             discount = float(p['discount_percentage'])
             final = float(p['unit_cost']) * (1 - discount / 100)
             prices.append(f"${final:.2f} ({discount}% OFF)")
        else:
             prices.append(f"${p['unit_cost']:.2f}")
    
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