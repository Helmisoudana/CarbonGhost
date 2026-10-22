-- À ajouter à infrastructure/init.sql (après les blocs mesures_db / carbone_db)
\c ia_db

CREATE TABLE IF NOT EXISTS anomalies (
    id             TEXT PRIMARY KEY,
    registered_at  TIMESTAMPTZ NOT NULL,
    machine_id     TEXT NOT NULL,
    "timestamp"    TIMESTAMPTZ NOT NULL,
    features       TEXT NOT NULL,
    score          DOUBLE PRECISION NOT NULL,
    severity       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_anomalies_machine_id ON anomalies (machine_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_machine_timestamp ON anomalies (machine_id, "timestamp" DESC);
