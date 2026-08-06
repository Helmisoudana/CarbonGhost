from pydantic import BaseModel
from datetime import datetime

class SecurityEvent(BaseModel):
    id:str
    timestamp:datetime
    device_id:str | None=None
    event_type: str
    description:str
    ip_adress:str | None=None
    user_id:str |None=None
    