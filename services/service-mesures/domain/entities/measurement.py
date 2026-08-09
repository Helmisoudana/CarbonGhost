# domain/entities/measurement.py — AUCUN import externe
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Measurement:
    machine_id: str
    device_id: str
    timestamp: datetime
    courant: float
    temperature: float
    vibration: float
    pression: float
    debit: float | None
    production_count: int
    id: str = field(default_factory=lambda: str(uuid4()))
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.courant < 0:
            raise ValueError("Le courant ne peut pas être négatif")

    @classmethod
    def from_dict(cls, data: dict) -> "Measurement":
        return cls(
            machine_id=data["machine_id"],
            device_id=data["device_id"],
            timestamp=data["timestamp"],
            courant=data["courant"],
            temperature=data["temperature"],
            vibration=data["vibration"],
            pression=data["pression"],
            debit=data.get("debit"),
            production_count=data["production_count"],
        )