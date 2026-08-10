from domain.entities.measurement import Measurement
from domain.ports.repositories.i_measurement_repository import IMeasurementRepository
from domain.ports.events.i_measurement_publisher import IMeasurementPublisher
from shared.contracts.sensor_measurement import SensorMeasurment

class ProcessMeasurementUseCase:
    def __init__(self,repository : IMeasurementRepository , publisher : IMeasurementPublisher):
        self.repository = repository
        self.publisher = publisher
    def execute(self, mesure :SensorMeasurment):
        measurement = Measurement.from_dict(mesure.model_dump())
        self.repository.save(measurement)
        self.publisher.publish(mesure)
        return measurement
