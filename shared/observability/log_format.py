from pydantic import BaseModel
from datetime import datetime

class LogEntry(BaseModel):
    timesyamp:datetime
    service_name:str
    level:str
    message:str
    trace_id:str | None=None
    machine_id: str | None=None
    extra : dict |None=None