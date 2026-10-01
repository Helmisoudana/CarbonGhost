from typing import Optional
from application.ports.hashing_service import IHashingService
from application.ports.email_notification_service import IEmailNotificationService
from domain.ports.repositories.repository import IUserRepository

from application.dtos.user_dto import CreateUserCommand, UserResponseDTO
from domain.exceptions import UserAlreadyExistsException, UserNotFoundException

class RegisterUserUseCase:
    """Cas d'utilisation pour l'enregistrement d'un nouvel utilisateur."""

    def __init__(self, user_repository:IUserRepository, hashing_service: IHashingService, email_notification_service: Optional[IEmailNotificationService] = None):
        self.user_repository = user_repository
        self.hashing_service = hashing_service
        self.email_service = email_notification_service

    def execute(self, command: CreateUserCommand) -> UserResponseDTO:
        """Exécute l'inscription étape par étape pour enregistrer un nouvel utilisateur.
        """
        # vérifier si l'utilisateur existe déjà
        existing_user = self.user_repository.get_by_email(command.email)
        if existing_user:
            raise UserAlreadyExistsException(f"Un utilisateur avec l'email {command.email} existe déjà.")

        # hacher le mot de passe
        hashed_password = self.hashing_service.hash_password(command.password)

        # créer l'utilisateur dans le repository
        new_user = self.user_repository.create(
            username=command.username,
            email=command.email,
            password=hashed_password,
            role=command.role,
            badge_id=command.badge_id
        )

        if self.email_service:
            self.email_service.send_notification(
                email=new_user.email,
                subject="Bienvenue sur CarbonGhost !",
                message=f"Bonjour {new_user.username}, votre compte a été créé avec succès."
            )
        # retourner le DTO de réponse
        return UserResponseDTO.model_validate(new_user)