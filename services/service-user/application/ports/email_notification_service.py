from abc import ABC, abstractmethod

class IEmailNotificationService(ABC):   
    """Interface pour le service de notification par email. Fournit des méthodes pour envoyer des emails."""
    
    @abstractmethod
    def send_welcome_email(self, to: str, username: str) -> None:
        """Envoie un email de bienvenue à l'adresse spécifiée aprés la création réussie d'un compte."""
        pass

    @abstractmethod
    def send_password_reset_email(self, to: str, reset_link: str) -> None:
        """Envoie un email contenant le lien ou le token de réinitialisation du mot de passe."""
        pass