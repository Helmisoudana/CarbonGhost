"""
Container du service IA : app FastAPI, exception handlers, health check,
router et câblage des dépendances. main.py ne fait que le lancer.
"""
import os
from contextlib import contextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.rest.ia_router import router as ia_router
from application.use_cases.DetectAnomalyUseCase import DetectAnomalyUseCase
from domain.exceptions.base_exceptions import (
    DomainException,
    NotFoundException,
    ValidationException,
    ConflictException,
    UnauthorizedException,
)
from domain.services.anomaly_detector import AnomalyDetector
from infrastructure.kafka.kafka_alert_publisher import KafkaAlertPublisher
from infrastructure.kafka.kafka_consumer import start_kafka_listener
from infrastructure.persistence.postgres.postgres_anomaly_repository import (
    PostgresAnomalyRepository,
)

SERVICE_NAME = "ia"

app = FastAPI(title="service-ia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_STATUS_BY_EXCEPTION = {
    NotFoundException: 404,
    ValidationException: 422,
    ConflictException: 409,
    UnauthorizedException: 401,
}


@app.exception_handler(DomainException)
def handle_domain_exception(request: Request, exc: DomainException):
    return JSONResponse(status_code=_STATUS_BY_EXCEPTION.get(type(exc), 400), content={"detail": str(exc)})


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}


app.include_router(ia_router)

# --- Configuration technique ---------------------------------------------

DATABASE_URL = os.environ["DATABASE_URL"]
KAFKA_BROKER = os.environ["KAFKA_BROKER"]

WINDOW_SIZE = int(os.environ.get("WINDOW_SIZE", 60))
MIN_SAMPLES = int(os.environ.get("MIN_SAMPLES", 20))
Z_THRESHOLD = float(os.environ.get("Z_THRESHOLD", 3.0))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

publisher = KafkaAlertPublisher(broker_address=KAFKA_BROKER)

# Unique pour la durée de vie du service : il garde les fenêtres glissantes en mémoire.
detector = AnomalyDetector(window_size=WINDOW_SIZE, min_samples=MIN_SAMPLES, z_threshold=Z_THRESHOLD)


@contextmanager
def get_detect_anomaly_use_case():
    """Utilisé par le consumer Kafka."""
    session = SessionLocal()
    try:
        yield DetectAnomalyUseCase(
            repository=PostgresAnomalyRepository(session),
            publisher=publisher,
            detector=detector,
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_anomaly_repository():
    """Utilisé par api/rest/ia_router.py pour les lectures seules."""
    session = SessionLocal()
    try:
        yield PostgresAnomalyRepository(session)
    finally:
        session.close()


# --- Cycle de vie du consumer Kafka --------------------------------------

kafka_consumer = None


@app.on_event("startup")
def on_startup():
    global kafka_consumer
    kafka_consumer = start_kafka_listener(broker_address=KAFKA_BROKER)


@app.on_event("shutdown")
def on_shutdown():
    if kafka_consumer is not None:
        kafka_consumer.stop()
