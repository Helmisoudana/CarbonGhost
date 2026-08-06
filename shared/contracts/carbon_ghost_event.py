from pydantic import BaseModel
from datetime import datetime

class CarbonGhostEvent(BaseModel):
    id: str
    machine_id: str
    timestamp: datetime
    actual_energy_kwh: float
    expected_energy_kwh: float
    wasted_energy_kwh: float
    carbon_factor: float
    avoidable_co2_kg: float
    probable_cause: str
    confidence: float
    security_risk: str
    status: str
    recommendation: str
    