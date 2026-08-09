from abc import ABC , abstractmethod
from domain.entities.measurement import Measurement


class IMeasurementRepository(ABC):
     
    @abstractmethod
    def save(self, mesurment : Measurement) -> None:
        ...

    @abstractmethod
    def find_by_id(self, measurement_id: str) -> Measurement | None:
        ...

    @abstractmethod
    def find_by_machine(self, machine_id:str) -> list[Measurement] | None:
        ...

    @abstractmethod
    def delete_by_machine(self , machine_id) ->None:
        """ Opération destructive et irréversible"""
        ...





