from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AnomalyModel(Base):
    __tablename__ = "anomalies"

    id = Column(String, primary_key=True)
    registered_at = Column(DateTime(timezone=True), nullable=False)
    machine_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    features = Column(String, nullable=False)  # séparés par des virgules
    score = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
