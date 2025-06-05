CREATE TABLE IF NOT EXISTS test_data (
    record_id BIGINT PRIMARY KEY,
    uuid_text VARCHAR(36) NOT NULL,
    category INT NOT NULL,
    timestamp_col DATETIME NOT NULL,
    INDEX idx_category (category),
    INDEX idx_timestamp (timestamp_col)
);
