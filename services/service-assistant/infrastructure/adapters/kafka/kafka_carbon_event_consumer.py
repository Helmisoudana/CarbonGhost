import json
from typing import Callable

from confluent_kafka import Consumer
from domain.ports.events.i_carbon_event_consumer import ICarbonEventConsumer
from shared.contracts.carbon_ghost_event import CarbonGhostEvent

TOPIC = "assistant.requests"


class KafkaCarbonEventConsumer(ICarbonEventConsumer):
    def __init__(self, broker_address: str, group_id: str = "service-assistant"):
        self.consumer = Consumer({
            "bootstrap.servers": broker_address,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
        })
        self.consumer.subscribe([TOPIC])

    def consume(self, handler: Callable[[CarbonGhostEvent], None]) -> None:
        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Erreur Kafka: {msg.error()}")
                continue
            data = json.loads(msg.value().decode("utf-8"))
            event = CarbonGhostEvent(**data)
            handler(event)
