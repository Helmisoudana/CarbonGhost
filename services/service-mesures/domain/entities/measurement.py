from datetime import datetime , timezone
from uuid import uuid4
from pydantic import BaseModel,Field
from shared.contracts.sensor_measurement import SensorMeasurment

class Measurement(BaseModel):
    id:str=Field(default_factory=lambda:str(uuid4()))
    registered_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
    data:SensorMeasurment


    @classmethod
    def from_sensor_measurement(cls, mesure: SensorMeasurment):
        return cls(data=mesure)