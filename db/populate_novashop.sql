-- Limpiar tabla existente de stocks
TRUNCATE TABLE product_stocks RESTART IDENTITY;

-- Habilitar extensión para UUIDs si no existe
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Insertar Laptops
INSERT INTO product_stocks (
    id, product_id, product_name, product_sku, 
    supplier_id, supplier_name, -- Agregado supplier_id
    quantity_on_hand, quantity_available, quantity_reserved,
    unit_cost, total_value,
    warehouse_location, stock_status, is_active,
    created_at, last_updated_at
) VALUES 
(gen_random_uuid(), 'LAP-HP-001', 'Laptop HP Pavilion 15 (Intel Core i5, 8GB RAM, 512GB SSD)', 'HP-PAV-15', 'SUP-HP-001', 'HP Distributor', 15, 15, 0, 750.00, 11250.00, 'Mesón Central, Zona HP', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'LAP-DELL-001', 'Laptop Dell Inspiron 3520 (Intel Core i5, 15.6" FHD)', 'DELL-INS-3520', 'SUP-DELL-001', 'Dell Official', 10, 10, 0, 680.00, 6800.00, 'Mesón Central, Zona Dell', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'LAP-MAC-001', 'MacBook Air M2 (Chip M2, 13.6", 256GB SSD, Midnight)', 'APPLE-AIR-M2', 'SUP-APPLE-001', 'Apple Inc.', 8, 8, 0, 1199.00, 9592.00, 'Isla Apple', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'LAP-MAC-002', 'MacBook Pro 14 M3 (Chip M3 Pro, 14", Space Black)', 'APPLE-PRO-M3', 'SUP-APPLE-001', 'Apple Inc.', 5, 5, 0, 1899.00, 9495.00, 'Isla Apple', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'LAP-ASUS-001', 'Laptop Asus TUF Gaming (Ryzen 7, RTX 3050, 144Hz)', 'ASUS-TUF-G', 'SUP-ASUS-001', 'Asus Gaming', 12, 12, 0, 950.00, 11400.00, 'Mesón Central, Zona Gaming', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'LAP-LEN-001', 'Laptop Lenovo IdeaPad 3 (Intel Core i3, Ideal estudiantes)', 'LEN-IDEA-3', 'SUP-LEN-001', 'Lenovo Corp', 20, 20, 0, 450.00, 9000.00, 'Mesón Lateral Izquierdo', 1, true, NOW(), NOW());

-- Insertar Celulares
INSERT INTO product_stocks (
    id, product_id, product_name, product_sku,
    supplier_id, supplier_name,
    quantity_on_hand, quantity_available, quantity_reserved,
    unit_cost, total_value,
    warehouse_location, stock_status, is_active,
    created_at, last_updated_at
) VALUES
(gen_random_uuid(), 'CEL-IPH-15', 'iPhone 15 128GB (Pantalla Super Retina XDR, USB-C)', 'IPH15-128', 'SUP-APPLE-001', 'Apple Inc.', 25, 25, 0, 899.00, 22475.00, 'Isla Apple, Vitrina Principal', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'CEL-IPH-14', 'iPhone 14 128GB (Chip A15 Bionic, Cámara dual)', 'IPH14-128', 'SUP-APPLE-001', 'Apple Inc.', 15, 15, 0, 799.00, 11985.00, 'Isla Apple, Vitrina Lateral', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'CEL-SAM-S24', 'Samsung Galaxy S24 Ultra (AI Phone, Stylus incluido, Titanio)', 'SAM-S24U', 'SUP-SAM-001', 'Samsung Electronics', 10, 10, 0, 1299.00, 12990.00, 'Stand Samsung, Pasillo Principal', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'CEL-SAM-A54', 'Samsung Galaxy A54 5G (Pantalla 120Hz, Resistente al agua)', 'SAM-A54', 'SUP-SAM-001', 'Samsung Electronics', 30, 30, 0, 350.00, 10500.00, 'Stand Samsung, Vitrina Media', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'CEL-XIA-RED', 'Xiaomi Redmi Note 13 (Cámara 108MP, Carga Rápida 33W)', 'XIA-NOTE13', 'SUP-XIA-001', 'Xiaomi Global', 40, 40, 0, 220.00, 8800.00, 'Stand Xiaomi, Pasillo Derecho', 1, true, NOW(), NOW());

-- Insertar Accesorios
INSERT INTO product_stocks (
    id, product_id, product_name, product_sku, 
    supplier_id, supplier_name,
    quantity_on_hand, quantity_available, quantity_reserved,
    unit_cost, total_value,
    warehouse_location, stock_status, is_active,
    created_at, last_updated_at
) VALUES
(gen_random_uuid(), 'ACC-APP-20W', 'Cargador Apple 20W (Adaptador de corriente USB-C)', 'APP-CHG-20W', 'SUP-APPLE-001', 'Apple Inc.', 50, 50, 0, 25.00, 1250.00, 'Pared Posterior, Accesorios', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'ACC-CAB-USB', 'Cable USB-C a Lightning (1 metro, Original)', 'APP-CBL-1M', 'SUP-APPLE-001', 'Apple Inc.', 50, 50, 0, 19.00, 950.00, 'Pared Posterior, Accesorios', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'ACC-FUN-MAG', 'Funda MagSafe iPhone 15 (Silicona, Varios Colores)', 'GEN-FUN-15', 'SUP-GEN-001', 'Generic Accs', 30, 30, 0, 49.00, 1470.00, 'Góndola 1, Accesorios Móviles', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'AUD-AIR-PRO', 'AirPods Pro 2da Gen (Cancelación de ruido activa, USB-C)', 'APP-AIR-PR2', 'SUP-APPLE-001', 'Apple Inc.', 20, 20, 0, 249.00, 4980.00, 'Isla Apple, Sección Audio', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'AUD-SAM-BUDS', 'Samsung Galaxy Buds2 Pro (Audio 360, Color Bora Purple)', 'SAM-BUDS-2P', 'SUP-SAM-001', 'Samsung Electronics', 15, 15, 0, 180.00, 2700.00, 'Stand Samsung, Sección Audio', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'PER-LOG-G203', 'Mouse Logitech G203 (Mouse Gamer, Luces RGB)', 'LOG-G203', 'SUP-LOG-001', 'Logitech', 25, 25, 0, 35.00, 875.00, 'Góndola 3, Periféricos', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'PER-RED-KEY', 'Teclado Mecánico Redragon (Switch Blue, Retroiluminado)', 'RED-K552', 'SUP-RED-001', 'Redragon', 15, 15, 0, 55.00, 825.00, 'Góndola 3, Periféricos', 1, true, NOW(), NOW());

-- Insertar Impresoras
INSERT INTO product_stocks (
    id, product_id, product_name, product_sku, 
    supplier_id, supplier_name,
    quantity_on_hand, quantity_available, quantity_reserved,
    unit_cost, total_value,
    warehouse_location, stock_status, is_active,
    created_at, last_updated_at
) VALUES
(gen_random_uuid(), 'IMP-EPS-L32', 'Impresora Epson EcoTank L3250 (Sistema continuo, WiFi)', 'EPS-L3250', 'SUP-EPS-001', 'Epson', 8, 8, 0, 210.00, 1680.00, 'Pasillo 4, Zona Impresión', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'IMP-HP-DJ', 'Impresora HP DeskJet Ink Advantage (Multifunción básica, Económica)', 'HP-DJ-INK', 'SUP-HP-001', 'HP Distributor', 12, 12, 0, 85.00, 1020.00, 'Pasillo 4, Zona Impresión', 1, true, NOW(), NOW());

-- Insertar Gaming
INSERT INTO product_stocks (
    id, product_id, product_name, product_sku, 
    supplier_id, supplier_name,
    quantity_on_hand, quantity_available, quantity_reserved,
    unit_cost, total_value,
    warehouse_location, stock_status, is_active,
    created_at, last_updated_at
) VALUES
(gen_random_uuid(), 'CON-PS5-SLM', 'PlayStation 5 Slim (Edición Digital, 1TB SSD)', 'SONY-PS5-D', 'SUP-SONY-001', 'Sony Ent.', 10, 10, 0, 549.00, 5490.00, 'Zona Gaming, Vitrina Sony', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'CON-NSW-OLE', 'Nintendo Switch OLED (Pantalla 7 pulgadas, Dock Blanco)', 'NIN-SW-OLED', 'SUP-NIN-001', 'Nintendo', 15, 15, 0, 349.00, 5235.00, 'Zona Gaming, Vitrina Nintendo', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'CON-XBX-SRX', 'Xbox Series X (La Xbox más rápida y potente)', 'MS-XBOX-X', 'SUP-MS-001', 'Microsoft', 5, 5, 0, 599.00, 2995.00, 'Zona Gaming, Vitrina Xbox', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'ACC-PS5-CTL', 'Control DualSense PS5 (Haptic Feedback, Blanco)', 'SONY-DS-W', 'SUP-SONY-001', 'Sony Ent.', 20, 20, 0, 75.00, 1500.00, 'Zona Gaming, Accesorios Consolas', 1, true, NOW(), NOW());

-- Insertar Otros
INSERT INTO product_stocks (
    id, product_id, product_name, product_sku, 
    supplier_id, supplier_name,
    quantity_on_hand, quantity_available, quantity_reserved,
    unit_cost, total_value,
    warehouse_location, stock_status, is_active,
    created_at, last_updated_at
) VALUES
(gen_random_uuid(), 'TAB-IPA-9GN', 'iPad 9na Gen (10.2 pulgadas, A13 Bionic)', 'APP-IPAD-9', 'SUP-APPLE-001', 'Apple Inc.', 12, 12, 0, 329.00, 3948.00, 'Isla Apple, Zona iPads', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'TAB-SAM-S9FE', 'Samsung Galaxy Tab S9 FE (Incluye S-Pen, Resistente al agua)', 'SAM-TAB-S9', 'SUP-SAM-001', 'Samsung Electronics', 8, 8, 0, 450.00, 3600.00, 'Mesón Lateral Derecho', 1, true, NOW(), NOW()),
(gen_random_uuid(), 'WER-APP-WSE', 'Apple Watch SE (Caja de aluminio, GPS)', 'APP-WATCH-SE', 'SUP-APPLE-001', 'Apple Inc.', 15, 15, 0, 249.00, 3735.00, 'Isla Apple, Wearables', 1, true, NOW(), NOW());
