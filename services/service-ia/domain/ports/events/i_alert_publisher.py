from abc import ABC, abstractmethod

from shared.contracts.alert import Alert


class IAlertPublisher(ABC):

    @abstractmethod
    def publish(self, alert: Alert) -> None:
        """Publie une alerte pour les autres services (assistant, dashboard)."""
        ...
