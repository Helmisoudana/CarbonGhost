from abc import ABC, abstractmethod

from domain.entities.anomaly import Anomaly


class IAnomalyRepository(ABC):

    @abstractmethod
    def save(self, anomaly: Anomaly) -> None:
        ...

    @abstractmethod
    def find_by_id(self, anomaly_id: str) -> Anomaly | None:
        ...

    @abstractmethod
    def find_by_machine(self, machine_id: str) -> list[Anomaly]:
        ...
