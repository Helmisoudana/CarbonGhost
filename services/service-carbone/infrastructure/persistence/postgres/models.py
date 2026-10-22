from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CarbonEventModel(Base):
    __tablename__ = "carbon_events"

    id = Column(String, primary_key=True)
    registered_at = Column(DateTime(timezone=True), nullable=False)
    machine_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    actual_energy_kwh = Column(Float, nullable=False)
    expected_energy_kwh = Column(Float, nullable=False)
    carbon_factor = Column(Float, nullable=False)
    probable_cause = Column(String, nullable=False, default="unknown")
    confidence = Column(Float, nullable=False, default=0.0)
    security_risk = Column(String, nullable=False, default="unknown")
    status = Column(String, nullable=False, default="pending_analysis")
    recommendation = Column(String, nullable=True)
