from sqlalchemy import Column, String, Float,Integer,DateTime
from sqlalchemy.orm import declarative_base

Base=declarative_base()

class MeasurementModel(Base):
    __tablename__="mesures"

    id=Column(String,primary_key=True)
    registered_at=Column(DateTime(timezone=True),nullable=False)
    machine_id=Column(String,nullable=False,index=True)
    device_id=Column(String,nullable=False)
    timestamp=Column(DateTime(timezone=True),nullable=False)
    courant=Column(Float,nullable=False)
    temperature=Column(Float,nullable=False)
    vibration=Column(Float,nullable=False)
    pression=Column(Float,nullable=False)
    debit=Column(Float,nullable=True)
    production_count=Column(Float,nullable=True)