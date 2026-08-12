from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID 

from domain.entities.user import User

class IUserRepository(ABC):

    @abstractmethod
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def save_user(self, user: User) -> User:
        #crée un nouvel utilisateur ou met à jour un utilisateur existant
        pass

    @abstractmethod
    def update_user(self, user: User) -> User:
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        pass