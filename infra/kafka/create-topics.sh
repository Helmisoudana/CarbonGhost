#!/bin/bash
set -e

BROKER="kafka:9092"

echo "Attente que Kafka soit pret..."
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
  echo " topic $name cree (partitions=$partitions, replication=$replication)"
}

create_topic "measures.raw" 3 1
create_topic "carbon.events" 3 1
create_topic "ia.anomalies" 3 1
create_topic "assistant.requests" 3 1
create_topic "assistant.explanations" 3 1

echo "Tous les topics sont prets."
