from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities.anomaly import Anomaly
from domain.ports.repositories.i_anomaly_repository import IAnomalyRepository
from infrastructure.persistence.postgres.models import AnomalyModel


class PostgresAnomalyRepository(IAnomalyRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, anomaly: Anomaly) -> None:
        self.session.add(AnomalyModel(
            id=anomaly.id,
            registered_at=anomaly.registered_at,
            machine_id=anomaly.machine_id,
            timestamp=anomaly.timestamp,
            features=",".join(anomaly.features),
            score=anomaly.score,
            severity=anomaly.severity,
        ))
        self.session.commit()

    def find_by_id(self, anomaly_id: str) -> Anomaly | None:
        model = self.session.get(AnomalyModel, anomaly_id)
        return self._to_entity(model) if model else None

    def find_by_machine(self, machine_id: str) -> list[Anomaly]:
        stmt = (
            select(AnomalyModel)
            .where(AnomalyModel.machine_id == machine_id)
            .order_by(AnomalyModel.timestamp.desc())
        )
        return [self._to_entity(m) for m in self.session.scalars(stmt).all()]

    @staticmethod
    def _to_entity(m: AnomalyModel) -> Anomaly:
        return Anomaly(
            id=m.id,
            registered_at=m.registered_at,
            machine_id=m.machine_id,
            timestamp=m.timestamp,
            features=m.features.split(","),
            score=m.score,
            severity=m.severity,
        )
