import json
from confluent_kafka import Producer
from domain.ports.events.i_assistant_result_publisher import IAssistantResultPublisher

TOPIC = "assistant.explanations"


class KafkaAssistantResultPublisher(IAssistantResultPublisher):
    def __init__(self, broker_address: str):
        self.producer = Producer({"bootstrap.servers": broker_address})

    def publish(self, machine_id: str, explanation: str) -> None:
        payload = json.dumps({
            "machine_id": machine_id,
            "explanation": explanation,
        }).encode("utf-8")
        self.producer.produce(topic=TOPIC, value=payload)
        self.producer.flush()