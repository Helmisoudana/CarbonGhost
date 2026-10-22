from abc import ABC, abstractmethod

from shared.contracts.carbon_ghost_event import CarbonGhostEvent


class ICarbonEventPublisher(ABC):

    @abstractmethod
    def publish(self, event: CarbonGhostEvent) -> None:
        """Publie un événement carbone pour que d'autres services (service-ia) le consomment."""
        ...
