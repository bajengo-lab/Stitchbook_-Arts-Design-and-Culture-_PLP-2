
-- Table to store customer contact details
CREATE TABLE IF NOT EXISTS customers (
    phone VARCHAR(10) PRIMARY KEY,
    name VARCHAR(12) UNIQUE NOT NULL,
    date_registered DATE NOT NULL
);

-- Table to store clothing orders linked to a customer phone number
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_phone VARCHAR(10) NOT NULL,
    clothing_type VARCHAR(10) NOT NULL,
    measurements VARCHAR(50) NOT NULL,
    delivery_date DATE NOT NULL,
    total_price INT NOT NULL,
    deposit_paid INT NOT NULL,
    status VARCHAR(12) NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (customer_phone) REFERENCES customers(phone)
);
