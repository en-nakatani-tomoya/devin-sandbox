CREATE TABLE IF NOT EXISTS test_data (
    record_id BIGINT PRIMARY KEY,
    uuid_text VARCHAR(36) NOT NULL,
    category INTEGER NOT NULL,
    timestamp_col TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_category ON test_data(category);
CREATE INDEX IF NOT EXISTS idx_timestamp ON test_data(timestamp_col);
