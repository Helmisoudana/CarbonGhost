import json
import threading

from confluent_kafka import Consumer
from pydantic import ValidationError

from shared.contracts.sensor_measurement import SensorMeasurment
from shared.observability.logger import get_logger

log = get_logger("ia")

TOPIC = "measures.raw"


class MeasuresConsumer:
    """Consomme measures.raw et déclenche DetectAnomalyUseCase pour chaque mesure valide."""

    def __init__(self, broker_address: str, group_id: str = "service-ia"):
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
        from container import get_detect_anomaly_use_case  # import tardif (circulaire)

        while self._running:
            msg = self._consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                log("WARNING", "Erreur Kafka", extra={"erreur": str(msg.error())})
                continue

            try:
                mesure = SensorMeasurment(**json.loads(msg.value().decode("utf-8")))
            except (json.JSONDecodeError, UnicodeDecodeError, ValidationError) as e:
                log("WARNING", "Message ignoré : invalide", extra={"erreur": str(e)})
                continue

            try:
                with get_detect_anomaly_use_case() as use_case:
                    anomaly = use_case.execute(mesure)
                if anomaly:
                    log("WARNING", "Anomalie détectée", machine_id=mesure.machine_id)
            except Exception as e:  # un message en échec ne doit pas tuer le thread
                log("ERROR", "Échec détection", extra={"erreur": str(e)})


def start_kafka_listener(broker_address: str) -> MeasuresConsumer:
    consumer = MeasuresConsumer(broker_address)
    consumer.start()
    return consumer
