# domain/entities/carbon_event.py — AUCUN import externe (FastAPI, SQLAlchemy, Kafka...)
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class CarbonEvent:
    """
    Un écart de consommation, traduit en carbone évitable, pour une
    machine et un instant donnés.

    Le "pourquoi" (probable_cause, confidence, security_risk,
    recommendation) n'est PAS calculé ici : c'est le rôle de
    service-ia, en aval, qui consomme carbon.events et enrichit
    l'événement. À la création par service-carbone, ces champs restent
    à leurs valeurs par défaut ("inconnu") et status="pending_analysis".
    """

    machine_id: str
    timestamp: datetime
    actual_energy_kwh: float
    expected_energy_kwh: float
    carbon_factor: float

    id: str = field(default_factory=lambda: str(uuid4()))
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    probable_cause: str = "unknown"
    confidence: float = 0.0
    security_risk: str = "unknown"
    status: str = "pending_analysis"
    recommendation: str = ""

    def __post_init__(self):
        if self.actual_energy_kwh < 0:
            raise ValueError("actual_energy_kwh ne peut pas être négatif")
        if self.expected_energy_kwh < 0:
            raise ValueError("expected_energy_kwh ne peut pas être négatif")
        if self.carbon_factor < 0:
            raise ValueError("carbon_factor ne peut pas être négatif")

    @property
    def wasted_energy_kwh(self) -> float:
        """Énergie gaspillée. Jamais négative : un déficit n'est pas un gaspillage."""
        return max(0.0, self.actual_energy_kwh - self.expected_energy_kwh)

    @property
    def avoidable_co2_kg(self) -> float:
        return round(self.wasted_energy_kwh * self.carbon_factor, 4)

    @classmethod
    def from_dict(cls, data: dict) -> "CarbonEvent":
        return cls(
            machine_id=data["machine_id"],
            timestamp=data["timestamp"],
            actual_energy_kwh=data["actual_energy_kwh"],
            expected_energy_kwh=data["expected_energy_kwh"],
            carbon_factor=data["carbon_factor"],
        )
