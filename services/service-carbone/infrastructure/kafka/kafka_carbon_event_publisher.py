import json
from confluent_kafka import Producer

from domain.ports.events.i_carbon_event_publisher import ICarbonEventPublisher
from shared.contracts.carbon_ghost_event import CarbonGhostEvent

TOPIC = "carbon.events"


class KafkaCarbonEventPublisher(ICarbonEventPublisher):
    def __init__(self, broker_address: str):
        self.producer = Producer({"bootstrap.servers": broker_address})

    def publish(self, event: CarbonGhostEvent) -> None:
        payload = json.dumps(event.model_dump(mode="json")).encode("utf-8")
        self.producer.produce(topic=TOPIC, value=payload)
        self.producer.flush()
