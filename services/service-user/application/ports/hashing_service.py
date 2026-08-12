from abc import ABC, abstractmethod

class IHashingService(ABC):
    """Interface pour le service de hachage. Fournit des méthodes pour hasher et vérifier les mots de passe."""
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hache un mot de passe."""
        pass

    @abstractmethod
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Vérifie si un mot de passe correspond au hash stocké."""
        pass