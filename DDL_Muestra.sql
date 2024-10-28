-- Tabla de usuarios (SIN ERROR)
CREATE TABLE users (
    user_id INT NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

-- Tabla de productos (SIN ERROR)
CREATE TABLE products (
    product_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id)
);

-- Tabla de categorías de productos (SIN ERROR)
CREATE TABLE categories (
    category_id INT NOT NULL,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (category_id)
);

-- Tabla de pedidos (ERROR: Clave foránea implícita en vez de explícita, debería referirse a `user_id`)
CREATE TABLE orders (
    order_id INT NOT NULL,
    user INT NOT NULL, -- ERROR: debería ser user_id como clave foránea explícita
    total DECIMAL(10, 2) NOT NULL CHECK (total >= 0),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id)
);

-- Tabla de detalles de pedidos (ERROR: Relación implícita, y error de cardinalidad uno a muchos)
CREATE TABLE order_details (
    order_detail_id INT NOT NULL,
    order_id INT NOT NULL, -- ERROR: No tiene clave foránea explícita a la tabla orders
    product INT NOT NULL, -- ERROR: implícito, debería ser product_id
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_detail_id)
);

-- Tabla de pagos (ERROR: Relación implícita y posible relación uno a uno mal definida)
CREATE TABLE payments (
    payment_id INT NOT NULL,
    order INT NOT NULL, -- ERROR: implícito, debería ser order_id como clave foránea explícita
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (payment_id)
);

-- Tabla de producto-categoría (ERROR: Relación muchos a muchos mal implementada)
CREATE TABLE product_categories (
    product_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (product_id), -- ERROR: debería ser clave compuesta de product_id y category_id
    FOREIGN KEY (product_id) REFERENCES products (product_id),
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
);

-- Tabla de envío (ERROR: No tiene clave foránea explícita a la tabla users)
CREATE TABLE shipping_addresses (
    address_id INT NOT NULL,
    user INT NOT NULL, -- ERROR: implícito, debería ser user_id
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    PRIMARY KEY (address_id)
);
