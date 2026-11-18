-- Tables: customers, orders. Owner: Mohammed.
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    clothing_type VARCHAR(50) NOT NULL,
    measurements TEXT,
    delivery_date DATE NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    deposit DECIMAL(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    tailor_number VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);