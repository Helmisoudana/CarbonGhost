from pydantic import BaseModel
from datetime import datetime

class Alert(BaseModel):
    id;str
    machine_id: str
    timestamp: datetime
    type:str
    severity:str
    message:str