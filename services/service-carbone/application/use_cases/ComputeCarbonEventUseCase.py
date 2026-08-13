from domain.entities.carbon_event import CarbonEvent
from domain.ports.repositories.i_carbon_event_repository import ICarbonEventRepository
from domain.ports.events.i_carbon_event_publisher import ICarbonEventPublisher
from domain.services.energy_estimator import EnergyEstimator
from shared.contracts.sensor_measurement import SensorMeasurment
from shared.contracts.carbon_ghost_event import CarbonGhostEvent


class ComputeCarbonEventUseCase:
    """
    Besoin métier : "à partir d'une mesure capteur, déterminer combien
    d'énergie a été gaspillée et combien de CO2 aurait pu être évité."

    """

    def __init__(
        self,
        repository: ICarbonEventRepository,
        publisher: ICarbonEventPublisher,
        estimator: EnergyEstimator,
        carbon_factor: float,
    ):
        self.repository = repository
        self.publisher = publisher
        self.estimator = estimator
        self.carbon_factor = carbon_factor

    def execute(self, mesure: SensorMeasurment) -> CarbonEvent:
        actual = self.estimator.estimate_actual_energy_kwh(mesure.courant)
        expected = self.estimator.estimate_expected_energy_kwh(mesure.production_count)

        event = CarbonEvent(
            machine_id=mesure.machine_id,
            timestamp=mesure.timestamp,
            actual_energy_kwh=actual,
            expected_energy_kwh=expected,
            carbon_factor=self.carbon_factor,
        )

        self.repository.save(event)
        self.publisher.publish(self._to_contract(event))
        return event

    @staticmethod
    def _to_contract(event: CarbonEvent) -> CarbonGhostEvent:
        return CarbonGhostEvent(
            id=event.id,
            machine_id=event.machine_id,
            timestamp=event.timestamp,
            actual_energy_kwh=event.actual_energy_kwh,
            expected_energy_kwh=event.expected_energy_kwh,
            wasted_energy_kwh=event.wasted_energy_kwh,
            carbon_factor=event.carbon_factor,
            avoidable_co2_kg=event.avoidable_co2_kg,
            probable_cause=event.probable_cause,
            confidence=event.confidence,
            security_risk=event.security_risk,
            status=event.status,
            recommendation=event.recommendation,
        )