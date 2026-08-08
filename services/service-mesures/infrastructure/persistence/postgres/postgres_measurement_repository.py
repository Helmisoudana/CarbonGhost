from sqlalchemy import select,delete
from sqlalchemy.orm import Session

from domain.entities.measurement import Measurement
from domain.ports.events.i_measurement_publisher import IMeasurementPublisher
from domain.ports.repositories.i_measurement_repository import IMeasurementRepository
from shared.contracts.sensor_measurement import SensorMeasurment
from infrastructure.persistence.postgres.models import MeasurementModel


class PostgresMeasurementRepository(IMeasurementRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self , measurement: Measurement ) -> None:
        data = measurement.data
        model = MeasurementModel(
            id=measurement.id,
            registered_at=measurement.registered_at,
            machine_id=measurement.data.machine_id,
            device_id=measurement.data.device_id,
            timestamp=measurement.data.timestamp,
            courant=measurement.data.courant,
            temperature=measurement.data.temperature,
            vibration=measurement.data.vibration,
            pression=measurement.data.pression,
            debit=measurement.data.debit,
            production_count=measurement.data.production_count,
        )
        self.session.add(model)
        self.session.commit()

    def find_by_id(self, measurement_id: str) ->Measurement | None:
        model=self.session.get(MeasurementModel , measurement_id)
        return self._to_entity(model) if model else None

    def find_by_machine(self, machine_id : str) -> list[Measurement] | None :
        stmt =(
            select(MeasurementModel)
            .where(MeasurementModel.machine_id == machine_id)
            .order_by(MeasurementModel.timestamp.desc())
        )
        models=self.session.scalars(stmt).all()
        return[self._to_entity(m) for m in models]


        
    def delete_by_machine(self, machine_id: str) -> int:
        stmt = delete(MeasurementModel).where(MeasurementModel.machine_id == machine_id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount


    def _to_entity(self, model: MeasurementModel) -> Measurement:
        mesure = SensorMeasurment(
            machine_id=model.machine_id,
            device_id=model.device_id,
            timestamp=model.timestamp,
            courant=model.courant,
            temperature=model.temperature,
            vibration=model.vibration,
            pression=model.pression,
            debit=model.debit,
            production_count=model.production_count,
        )
        return Measurement(id=model.id, registered_at=model.registered_at, data=mesure)

   


