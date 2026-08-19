from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CarbonEvent:
    id: int
    machine_id: str
    timestamp: datetime

    actual_energy_kwh: Optional[float] = None
    expected_energy_kwh: Optional[float] = None
    surconsommation_pct: Optional[float] = None
    avoidable_co2_kg: Optional[float] = None

    probable_cause: Optional[str] = None
    confidence: Optional[float] = None
    recommendation: Optional[str] = None