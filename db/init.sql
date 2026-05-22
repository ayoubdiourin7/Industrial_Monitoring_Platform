CREATE TABLE IF NOT EXISTS readings (
    id SERIAL PRIMARY KEY,
    machine_id VARCHAR(50) NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    vibration DOUBLE PRECISION NOT NULL,
    pressure DOUBLE PRECISION NOT NULL,
    is_anomaly BOOLEAN NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_readings_machine_id ON readings(machine_id);
CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings(timestamp);
