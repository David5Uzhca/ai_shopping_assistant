CREATE TABLE IF NOT EXISTS product_offers (
    offer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(255) NOT NULL,
    discount_percentage DECIMAL(5, 2) NOT NULL,
    description VARCHAR(255),
    start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_offers_product_id ON product_offers(product_id);

TRUNCATE TABLE product_offers RESTART IDENTITY;

INSERT INTO product_offers (product_id, discount_percentage, description) VALUES
('CEL-IPH-15', 5.00, 'Descuento Apple Lovers'),
('CEL-IPH-14', 12.00, 'Liquidación de stock'),
('CEL-SAM-S24', 8.00, 'Promo Lanzamiento'),
('CEL-SAM-A54', 15.00, 'Super Oferta Calidad-Precio'),
('CEL-XIA-RED', 10.00, 'Xiaomi Week');

INSERT INTO users (user_id, email, password_hash, first_name, last_name, phone, role)
VALUES (
    '658efd3d-4d37-448a-830f-bf8216ce225f',
    'juandaviduzhca@hotmail.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxv96pPE8BWNhiynKEx.5x5.5x5',
    'Juan',
    'David',
    '59399569307',
    'customer'
) ON CONFLICT (user_id) DO NOTHING;
