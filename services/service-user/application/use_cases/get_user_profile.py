from domain.ports.repositories.repository import IUserRepository
from application.dtos.user_dto import UserResponseDTO
from domain.exceptions import UserNotFoundException


class GetUserProfileUseCase:
    """Cas d'utilisation pour récupérer le profil d'un utilisateur."""

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: str) -> UserResponseDTO:
        """Récupère l'utilisateur par son ID."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"Utilisateur avec l'ID {user_id} introuvable.")

        return UserResponseDTO.model_validate(user)