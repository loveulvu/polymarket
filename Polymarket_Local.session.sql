-- 1. 删除结构不正确的旧表
-- 2. 重新创建，确保包含 recorded_at
CREATE TABLE market_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token_id VARCHAR(255),
    price DECIMAL(10, 4),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);