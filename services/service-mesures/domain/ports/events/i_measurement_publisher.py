from abc import ABC, abstractmethod

from shared.contracts.sensor_measurement import SensorMeasurment


class IMeasurementPublisher(ABC):
    

    @abstractmethod
    def publish(self, mesure: SensorMeasurment) -> None:
        """Publie une mesure capteur pour que d'autres services la consomment."""
        ...