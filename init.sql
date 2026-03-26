CREATE TABLE IF NOT EXISTS polymarket_prices_optimized (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_title VARCHAR(500) NOT NULL,
    yes_price DECIMAL(6, 4) NOT NULL,
    no_price DECIMAL(6, 4) NOT NULL,
    diff_value DECIMAL(6, 4) NOT NULL,
    volume DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_title (question_title(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;