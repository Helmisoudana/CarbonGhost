from abc import ABC, abstractmethod

from domain.entities.carbon_event import CarbonEvent


class ICarbonEventRepository(ABC):

    @abstractmethod
    def save(self, event: CarbonEvent) -> None:
        ...

    @abstractmethod
    def find_by_id(self, event_id: str) -> CarbonEvent | None:
        ...

    @abstractmethod
    def find_by_machine(self, machine_id: str) -> list[CarbonEvent]:
        ...

    @abstractmethod
    def delete_by_machine(self, machine_id: str) -> None:
        """Opération destructive et irréversible"""
        ...
