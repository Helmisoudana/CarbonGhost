import json
from confluent_kafka import Producer

from domain.ports.events.i_alert_publisher import IAlertPublisher
from shared.contracts.alert import Alert

TOPIC = "alerts"


class KafkaAlertPublisher(IAlertPublisher):
    def __init__(self, broker_address: str):
        self.producer = Producer({"bootstrap.servers": broker_address})

    def publish(self, alert: Alert) -> None:
        payload = json.dumps(alert.model_dump(mode="json")).encode("utf-8")
        self.producer.produce(topic=TOPIC, value=payload)
        self.producer.flush()
