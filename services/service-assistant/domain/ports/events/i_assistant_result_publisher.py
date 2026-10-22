from abc import ABC, abstractmethod


class IAssistantResultPublisher(ABC):

    @abstractmethod
    def publish(self, machine_id: str, explanation: str) -> None:
        pass
