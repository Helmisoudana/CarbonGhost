import json

import paho.mqtt.client as mqtt
from pydantic import ValidationError

from shared.contracts.sensor_measurement import SensorMeasurment
from shared.observability.logger import get_logger

log = get_logger("mesures")

TOPIC = "capteurs/mesures"


def on_connect(client, userdata, flags, reason_code, properties=None):
    log("INFO", "Connecté au broker MQTT", extra={"reason_code": str(reason_code)})
    client.subscribe(TOPIC)
    log("INFO", f"Abonné au topic {TOPIC}")


def on_message(client, userdata, msg):

    from container import get_process_measurement_use_case

    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        log("WARNING", "Message MQTT ignoré : JSON invalide", extra={"topic": msg.topic})
        return

    try:
        mesure = SensorMeasurment(**payload)
    except ValidationError as e:
        log("WARNING", "Message MQTT ignoré : ne correspond pas à SensorMeasurment", extra={"erreur": str(e)})
        return

    with get_process_measurement_use_case() as use_case:
        use_case.execute(mesure)
    log("INFO", "Mesure traitée", machine_id=mesure.machine_id)


def start_mqtt_listener(broker_address: str, broker_port: int = 1883) -> mqtt.Client:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address, broker_port)
    client.loop_start()

    log("INFO", "Listener MQTT démarré", extra={"broker": f"{broker_address}:{broker_port}"})
    return client