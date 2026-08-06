from pydantic import BaseModel
from datetime import datetime


class SensorMeasurment(BaseModel):
    machine_id: str
    device_id: str
    timestamp : datetime
    courant: float
    temperature: float
    vibration: float
    pression: float
    debit: float | None= None
    production_count: int