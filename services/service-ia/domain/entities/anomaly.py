# AUCUN import externe (FastAPI, SQLAlchemy, Kafka...)
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Anomaly:

    machine_id: str
    timestamp: datetime
    features: list[str]   # capteurs hors norme, ex: ["vibration", "courant"]
    score: float          # z-score maximal observé
    severity: str         # "medium" | "high" | "critical"

    id: str = field(default_factory=lambda: str(uuid4()))
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.features:
            raise ValueError("une anomalie doit avoir au moins un capteur fautif")

    @property
    def message(self) -> str:
        return f"Anomalie sur {self.machine_id} : " + ", ".join(self.features) + f" (score {self.score:.1f})"
