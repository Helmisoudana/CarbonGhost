from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from domain.entities.carbon_event import CarbonEvent
from domain.ports.repositories.i_carbon_event_repository import ICarbonEventRepository
from infrastructure.persistence.postgres.models import CarbonEventModel


class PostgresCarbonEventRepository(ICarbonEventRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, event: CarbonEvent) -> None:
        model = CarbonEventModel(
            id=event.id,
            registered_at=event.registered_at,
            machine_id=event.machine_id,
            timestamp=event.timestamp,
            actual_energy_kwh=event.actual_energy_kwh,
            expected_energy_kwh=event.expected_energy_kwh,
            carbon_factor=event.carbon_factor,
            probable_cause=event.probable_cause,
            confidence=event.confidence,
            security_risk=event.security_risk,
            status=event.status,
            recommendation=event.recommendation,
        )
        self.session.add(model)
        self.session.commit()

    def find_by_id(self, event_id: str) -> CarbonEvent | None:
        model = self.session.get(CarbonEventModel, event_id)
        return self._to_entity(model) if model else None

    def find_by_machine(self, machine_id: str) -> list[CarbonEvent]:
        stmt = (
            select(CarbonEventModel)
            .where(CarbonEventModel.machine_id == machine_id)
            .order_by(CarbonEventModel.timestamp.desc())
        )
        models = self.session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def delete_by_machine(self, machine_id: str) -> int:
        stmt = delete(CarbonEventModel).where(CarbonEventModel.machine_id == machine_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount

    def _to_entity(self, model: CarbonEventModel) -> CarbonEvent:
        return CarbonEvent(
            id=model.id,
            registered_at=model.registered_at,
            machine_id=model.machine_id,
            timestamp=model.timestamp,
            actual_energy_kwh=model.actual_energy_kwh,
            expected_energy_kwh=model.expected_energy_kwh,
            carbon_factor=model.carbon_factor,
            probable_cause=model.probable_cause,
            confidence=model.confidence,
            security_risk=model.security_risk,
            status=model.status,
            recommendation=model.recommendation,
        )
