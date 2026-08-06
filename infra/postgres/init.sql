-- init.sql
-- Exécuté automatiquement au premier démarrage du conteneur Postgres.
-- Crée une base dédiée par service (chaque service ne voit QUE sa base,
-- ce qui respecte l'architecture hexagonale : pas de base partagée entre
-- microservices).

CREATE DATABASE user_db;
CREATE DATABASE carbone_db;
CREATE DATABASE mesures_db;
CREATE DATABASE ia_db;
CREATE DATABASE assistant_db;
CREATE DATABASE factory_db;

-- Optionnel : un user applicatif par service, avec droits limités
-- à sa propre base uniquement.
-- CREATE USER user_service WITH PASSWORD 'changeme';
-- GRANT ALL PRIVILEGES ON DATABASE user_db TO user_service;
