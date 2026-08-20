from abc import ABC, abstractmethod

class ITokenService(ABC):
    """port d'interface pour la gestion des tokens de sécurité."""
    @abstractmethod
    def generate_token(self, data: dict) -> str:
        """Génère un token à partir d'un dictionnaire de données."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> dict: 
        """Vérifie la validité d'un token et renvoie son contenu (payload décodé).
        Lève une exception si le token est invalide ou expiré."""
        pass