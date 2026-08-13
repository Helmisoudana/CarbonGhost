#!/bin/bash
# create-topics.sh
# CrÃ©e les topics Kafka nÃ©cessaires au systÃ¨me. Ã€ lancer une fois que
# le conteneur Kafka est up (docker-compose exec kafka bash puis lancer
# ce script, ou via un conteneur "kafka-init" dÃ©diÃ© dans docker-compose).

set -e

BROKER="kafka:9092"

echo "Attente que Kafka soit prÃªt..."
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
  echo " topic $name crÃ©Ã© (partitions=$partitions, replication=$replication)"
}

# Ã‰vÃ©nements bruts remontÃ©s par service-mesures depuis MQTT
create_topic "measures.raw" 3 1

# Ã‰vÃ©nements carbone calculÃ©s, consommÃ©s par service-carbone -> service-ia
create_topic "carbon.events" 3 1

# Alertes/anomalies dÃ©tectÃ©es par service-ia
create_topic "ia.anomalies" 3 1

echo "Tous les topics sont prÃªts."
