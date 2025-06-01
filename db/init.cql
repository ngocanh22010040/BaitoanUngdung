-- Tạo keyspace
CREATE KEYSPACE IF NOT EXISTS iot_data WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

-- Sử dụng keyspace
USE iot_data;

-- Tạo bảng dữ liệu cảm biến
CREATE TABLE IF NOT EXISTS sensor_data (
  sensor_id TEXT,
  timestamp TIMESTAMP,
  temperature FLOAT,
  humidity FLOAT,
  light_level INT,
  PRIMARY KEY (sensor_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
