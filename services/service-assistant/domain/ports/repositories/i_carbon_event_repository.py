from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from domain.entities.carbon_event import CarbonEvent


class ICarbonEventRepository(ABC):

    @abstractmethod
    def get_recent_events(
        self,
        limit: int = 20
    ) -> List[CarbonEvent]:
        pass

    @abstractmethod
    def get_events_between(
        self,
        start: datetime,
        end: datetime
    ) -> List[CarbonEvent]:
        pass

    @abstractmethod
    def get_events_by_machine(
        self,
        machine_id: str,
        limit: int = 20
    ) -> List[CarbonEvent]:
        pass