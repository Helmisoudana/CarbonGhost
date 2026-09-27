from abc import ABC, abstractmethod
from typing import Callable
from shared.contracts.carbon_ghost_event import CarbonGhostEvent


class ICarbonEventConsumer(ABC):

    @abstractmethod
    def consume(self, handler: Callable[[CarbonGhostEvent], None]) -> None:
        pass
