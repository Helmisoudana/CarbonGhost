CREATE DATABASE user_db;
CREATE DATABASE carbone_db;
CREATE DATABASE mesures_db;
CREATE DATABASE ia_db;
CREATE DATABASE assistant_db;
CREATE DATABASE factory_db;


 
\c mesures_db
 
CREATE TABLE IF NOT EXISTS mesures (
    id                 TEXT PRIMARY KEY,
    registered_at      TIMESTAMPTZ NOT NULL,
    machine_id         TEXT NOT NULL,
    device_id          TEXT NOT NULL,
    "timestamp"        TIMESTAMPTZ NOT NULL,
    courant            DOUBLE PRECISION NOT NULL,
    temperature        DOUBLE PRECISION NOT NULL,
    vibration          DOUBLE PRECISION NOT NULL,
    pression           DOUBLE PRECISION NOT NULL,
    debit              DOUBLE PRECISION,
    production_count   INTEGER NOT NULL
);
 
CREATE INDEX IF NOT EXISTS idx_mesures_machine_id ON mesures (machine_id);
CREATE INDEX IF NOT EXISTS idx_mesures_machine_timestamp ON mesures (machine_id, "timestamp" DESC);

\c carbone_db

CREATE TABLE IF NOT EXISTS carbon_events (
    id                   TEXT PRIMARY KEY,
    registered_at        TIMESTAMPTZ NOT NULL,
    machine_id           TEXT NOT NULL,
    "timestamp"          TIMESTAMPTZ NOT NULL,
    actual_energy_kwh    DOUBLE PRECISION NOT NULL,
    expected_energy_kwh  DOUBLE PRECISION NOT NULL,
    carbon_factor        DOUBLE PRECISION NOT NULL,
    probable_cause       TEXT NOT NULL DEFAULT 'unknown',
    confidence           DOUBLE PRECISION NOT NULL DEFAULT 0,
    security_risk        TEXT NOT NULL DEFAULT 'unknown',
    status                TEXT NOT NULL DEFAULT 'pending_analysis',
    recommendation        TEXT
);

CREATE INDEX IF NOT EXISTS idx_carbon_events_machine_id ON carbon_events (machine_id);
CREATE INDEX IF NOT EXISTS idx_carbon_events_machine_timestamp ON carbon_events (machine_id, "timestamp" DESC);
