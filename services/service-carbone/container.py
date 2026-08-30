"""
Container du service carbone.
Regroupe tout ce qui est commun : app FastAPI, middlewares, exception
handlers, health check, et inclusion du router. C'est le seul fichier
qui assemble les dépendances : main.py ne fait que le lancer.
"""
import os
from contextlib import contextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.rest.carbone_router import router as carbone_router
from application.use_cases.ComputeCarbonEventUseCase import ComputeCarbonEventUseCase
from domain.services.energy_estimator import EnergyEstimator
from domain.exceptions.base_exceptions import (
    DomainException,
    NotFoundException,
    ValidationException,
    ConflictException,
    UnauthorizedException,
)
from infrastructure.persistence.postgres.postgres_carbon_event_repository import (
    PostgresCarbonEventRepository,
)
from infrastructure.kafka.kafka_carbon_event_publisher import KafkaCarbonEventPublisher
from infrastructure.kafka.kafka_consumer import start_kafka_listener

SERVICE_NAME = "carbone"

app = FastAPI(title="service-carbone")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Exception handlers : traduisent les exceptions de domain/exceptions ---
# en réponses HTTP. Aucun router n'a besoin de try/except.

_STATUS_BY_EXCEPTION = {
    NotFoundException: 404,
    ValidationException: 422,
    ConflictException: 409,
    UnauthorizedException: 401,
}


@app.exception_handler(DomainException)
def handle_domain_exception(request: Request, exc: DomainException):
    status_code = _STATUS_BY_EXCEPTION.get(type(exc), 400)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


# --- Health check commun à tous les services -------------------------------


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}


# --- Router spécifique au service ------------------------------------------

app.include_router(carbone_router)


# --- Configuration technique -------------------------------------------

DATABASE_URL = os.environ["DATABASE_URL"]
KAFKA_BROKER = os.environ["KAFKA_BROKER"]

# Facteur d'émission (kg CO2 / kWh) et hypothèses physiques du
# domain/services/energy_estimator.py : configurables par variable
# d'environnement, jamais codées en dur dans le domaine. Les valeurs par
# défaut ci-dessous sont des PLACEHOLDERS à ajuster avec l'équipe /
# les vraies données de l'usine.
CARBON_FACTOR_KG_PER_KWH = float(os.environ.get("CARBON_FACTOR_KG_PER_KWH", 0.5))
VOLTAGE = float(os.environ.get("MACHINE_VOLTAGE", 230))
POWER_FACTOR = float(os.environ.get("MACHINE_POWER_FACTOR", 0.9))
SAMPLING_INTERVAL_HOURS = float(os.environ.get("SAMPLING_INTERVAL_HOURS", 1 / 60))
EXPECTED_KWH_PER_UNIT = float(os.environ.get("EXPECTED_KWH_PER_UNIT", 0.1))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Le publisher Kafka est unique pour toute la durée de vie du service.
publisher = KafkaCarbonEventPublisher(broker_address=KAFKA_BROKER)

estimator = EnergyEstimator(
    voltage=VOLTAGE,
    power_factor=POWER_FACTOR,
    sampling_interval_hours=SAMPLING_INTERVAL_HOURS,
    expected_kwh_per_unit=EXPECTED_KWH_PER_UNIT,
)


@contextmanager
def get_compute_carbon_event_use_case():
    """
    Fournit un ComputeCarbonEventUseCase avec sa propre session
    SQLAlchemy, utilisé par le consumer Kafka
    (infrastructure/kafka/kafka_consumer.py) via
    `with get_compute_carbon_event_use_case() as use_case:`.
    """
    session = SessionLocal()
    try:
        repository = PostgresCarbonEventRepository(session)
        use_case = ComputeCarbonEventUseCase(
            repository=repository,
            publisher=publisher,
            estimator=estimator,
            carbon_factor=CARBON_FACTOR_KG_PER_KWH,
        )
        yield use_case
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_carbon_event_repository():
    """Utilisé par api/rest/carbone_router.py pour les lectures seules."""
    session = SessionLocal()
    try:
        yield PostgresCarbonEventRepository(session)
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
