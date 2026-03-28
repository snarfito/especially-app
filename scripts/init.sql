-- Extensiones necesarias para generación de UUIDs y búsquedas optimizadas
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. TABLA DE USUARIOS
-- Almacena credenciales y perfiles para Compradores, Socios Productores y Diseñadores
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    user_role VARCHAR(20) CHECK (user_role IN ('buyer', 'seller', 'designer')) DEFAULT 'buyer',
    city VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA DE PRODUCTOS BASE
-- Define el catálogo general: Camisetas (personalizables) o Artesanías (piezas auténticas)
CREATE TABLE products (
    product_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- Ej: 'Camisetas', 'Jabones', 'Mugs'
    base_price DECIMAL(12, 2) NOT NULL,
    is_customizable BOOLEAN DEFAULT FALSE, -- Identifica si admite el editor de diseño
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABLA DE DISEÑOS PERSONALIZADOS
-- Almacena el estado del canvas (Fabric.js) creado por el usuario
CREATE TABLE custom_designs (
    design_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    canvas_json JSONB NOT NULL, -- Almacena capas, filtros y posiciones del editor
    preview_image_url TEXT, -- URL de la miniatura generada para el carrito
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. TABLA DE PEDIDOS (ORDERS)
-- Orquesta la transacción entre Comprador y Socio Productor
CREATE TABLE orders (
    order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id UUID REFERENCES users(user_id),
    seller_id UUID REFERENCES users(user_id), -- Socio que acepta la producción
    status VARCHAR(30) CHECK (status IN ('pending', 'accepted', 'producing', 'shipped', 'delivered')),
    shipping_type VARCHAR(20) CHECK (shipping_type IN ('normal', 'urgent')), -- Logística urgente (3-6 días)
    total_amount DECIMAL(12, 2) NOT NULL,
    shipping_address TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. DETALLE DEL PEDIDO
-- Vincula productos específicos y sus diseños personalizados con la orden
CREATE TABLE order_items (
    item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(product_id),
    design_id UUID REFERENCES custom_designs(design_id), -- Opcional, solo si es personalizable
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(12, 2) NOT NULL, -- Precio al momento de la compra para histórico
    size VARCHAR(10), -- XS, S, M, L, XL, etc.
    color VARCHAR(30)
);

-- Índices para optimizar búsquedas frecuentes en el Marketplace
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_orders_buyer ON orders(buyer_id);
CREATE INDEX idx_orders_status ON orders(status);
