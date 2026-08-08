import json
from confluent_kafka import Producer
from domain.ports.events.i_measurement_publisher import IMeasurementPublisher
from shared.contracts.sensor_measurement import SensorMeasurment

TOPIC = "measures.raw"

class KafkaMeasurementPublisher(IMeasurementPublisher):
    def __init__(self,broker_address:str):
        self.producer=Producer({"bootstrap.services" : broker_address})

    def publish(self , mesure:SensorMeasurment)-> None:
        payload =json.dumps(mesure.model_dump(mode="json")).encode("utf-8")
        self.producer.produce(topic=TOPIC , value=payload)
        self.producer.flush()