import os
from contextlib import contextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.rest.mesures_router import router as mesures_router
from application.use_cases.ProcessMeasurementUseCase import ProcessMeasurementUseCase
from infrastructure.persistence.postgres.postgres_measurement_repository import (
    PostgresMeasurementRepository,
)
from infrastructure.kafka.kafka_measurement_publisher import KafkaMeasurementPublisher
from infrastructure.mqtt.mqtt_client import start_mqtt_listener



SERVICE_NAME = "mesures"

app = FastAPI(title="service-mesures")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health check ------------------------------------------------------


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}



app.include_router(mesures_router)



DATABASE_URL = os.environ["DATABASE_URL"]
KAFKA_BROKER = os.environ["KAFKA_BROKER"]
MQTT_BROKER = os.environ["MQTT_BROKER"]
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Le publisher Kafka, lui, est unique pour toute la durée de vie du service.
publisher = KafkaMeasurementPublisher(broker_address=KAFKA_BROKER)


def build_process_measurement_use_case() -> ProcessMeasurementUseCase:

    session = SessionLocal()
    repository = PostgresMeasurementRepository(session)
    return ProcessMeasurementUseCase(repository=repository, publisher=publisher)


@contextmanager
def get_process_measurement_use_case():
    """
    Fournit un ProcessMeasurementUseCase avec sa propre session SQLAlchemy,
    utilisé par le listener MQTT (infrastructure/mqtt/mqtt_client.py) via
    `with get_process_measurement_use_case() as use_case:`.

    La session est commit si tout se passe bien, rollback en cas d'erreur,
    puis fermée dans tous les cas.
    """
    session = SessionLocal()
    try:
        repository = PostgresMeasurementRepository(session)
        use_case = ProcessMeasurementUseCase(repository=repository, publisher=publisher)
        yield use_case
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# --- Cycle de vie du listener MQTT --------------------------------------

mqtt_client = None


@app.on_event("startup")
def on_startup():
    global mqtt_client
    mqtt_client = start_mqtt_listener(broker_address=MQTT_BROKER, broker_port=MQTT_PORT)


@app.on_event("shutdown")
def on_shutdown():
    if mqtt_client is not None:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()