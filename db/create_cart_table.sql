-- Tabla para el carrito de compras (una por usuario)
-- Se puede asumir que cada usuario tiene un carrito "activo".
-- O simplemente usamos user_id para buscar el carrito.

CREATE TABLE IF NOT EXISTS carts (
    cart_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'ordered', 'abandoned'
    CONSTRAINT unique_active_cart_per_user UNIQUE (user_id, status) 
    -- Esto forzaría a tener solo un carrito con status='active' si usamos partial index, 
    -- pero simplificaremos asumiendo que buscamos el último activo.
);

-- Tabla para los items del carrito
CREATE TABLE IF NOT EXISTS cart_items (
    item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
    product_id VARCHAR(255) NOT NULL, -- Referencia a product_stocks.product_id
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Evitar duplicados del mismo producto en el mismo carrito (mejor actualizar cantidad)
    CONSTRAINT unique_product_per_cart UNIQUE (cart_id, product_id)
);

-- Índices para búsqueda rápida
CREATE INDEX IF NOT EXISTS idx_carts_user_id ON carts(user_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id);
