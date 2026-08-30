import json
import threading

from confluent_kafka import Consumer
from pydantic import ValidationError

from shared.contracts.sensor_measurement import SensorMeasurment
from shared.observability.logger import get_logger

log = get_logger("carbone")

TOPIC = "measures.raw"


class MeasuresConsumer:
    """
    Consomme measures.raw et déclenche ComputeCarbonEventUseCase pour
    chaque mesure valide, dans un thread séparé (ne bloque pas FastAPI).

    Même raisonnement que le listener MQTT de service-mesures : le
    use case reste identique, seul le déclencheur change (Kafka au
    lieu d'HTTP/MQTT).
    """

    def __init__(self, broker_address: str, group_id: str = "service-carbone"):
        self._consumer = Consumer({
            "bootstrap.servers": broker_address,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
        })
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self):
        self._consumer.subscribe([TOPIC])
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        log("INFO", "Consumer Kafka démarré", extra={"topic": TOPIC})

    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=5)
        self._consumer.close()

    def _run(self):
        # Import tardif pour éviter un import circulaire avec container.py,
        # même pattern que infrastructure/mqtt/mqtt_client.py sur service-mesures.
        from container import get_compute_carbon_event_use_case

        while self._running:
            msg = self._consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                log("WARNING", "Erreur Kafka", extra={"erreur": str(msg.error())})
                continue

            try:
                payload = json.loads(msg.value().decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                log("WARNING", "Message Kafka ignoré : JSON invalide")
                continue

            try:
                mesure = SensorMeasurment(**payload)
            except ValidationError as e:
                log("WARNING", "Message Kafka ignoré : ne correspond pas à SensorMeasurment", extra={"erreur": str(e)})
                continue

            with get_compute_carbon_event_use_case() as use_case:
                use_case.execute(mesure)
            log("INFO", "Événement carbone calculé", machine_id=mesure.machine_id)


def start_kafka_listener(broker_address: str) -> MeasuresConsumer:
    consumer = MeasuresConsumer(broker_address)
    consumer.start()
    return consumer
