#!/bin/bash
# create-topics.sh
# Crée les topics Kafka nécessaires au système. À lancer une fois que
# le conteneur Kafka est up (docker-compose exec kafka bash puis lancer
# ce script, ou via un conteneur "kafka-init" dédié dans docker-compose).

set -e

BROKER="kafka:9092"

echo "Attente que Kafka soit prêt..."
until kafka-topics --bootstrap-server "$BROKER" --list > /dev/null 2>&1; do
  sleep 2
done

create_topic() {
  local name=$1
  local partitions=${2:-3}
  local replication=${3:-1}
  kafka-topics --bootstrap-server "$BROKER" \
    --create --if-not-exists \
    --topic "$name" \
    --partitions "$partitions" \
    --replication-factor "$replication"
  echo "✅ topic $name créé (partitions=$partitions, replication=$replication)"
}

# Événements bruts remontés par service-mesures depuis MQTT
create_topic "mesures.raw" 3 1

# Événements carbone calculés, consommés par service-carbone -> service-ia
create_topic "carbon.events" 3 1

# Alertes/anomalies détectées par service-ia
create_topic "ia.anomalies" 3 1

echo "Tous les topics sont prêts."
