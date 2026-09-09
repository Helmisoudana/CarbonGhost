from application.ports.hashing_service import IHashingService
from application.ports.token_service import ITokenService
from domain.ports.repositories.repository import IUserRepository

from application.dtos.user_dto import LoginUserCommand, TokenResponseDTO
from domain.exceptions import InvalidCredentialsException


class AuthenticateUserUseCase:
    """Cas d'utilisation pour la connexion et la génération de token JWT."""

    def __init__(
        self,
        user_repository: IUserRepository,
        hashing_service: IHashingService,
        token_service: ITokenService,
    ):
        self.user_repository = user_repository
        self.hashing_service = hashing_service
        self.token_service = token_service

    def execute(self, command: LoginUserCommand) -> TokenResponseDTO:
        """Vérifie les identifiants et renvoie le token."""
        # récupérer l'utilisateur
        user = self.user_repository.get_by_email(command.email)
        if not user:
            raise InvalidCredentialsException("Email ou mot de passe incorrect.")

        # vérifier le mot de passe
        is_valid = self.hashing_service.verify_password(command.password, user.password)
        if not is_valid:
            raise InvalidCredentialsException("Email ou mot de passe incorrect.")

        # générer le token JWT via le port Token
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
        token = self.token_service.generate_token(payload)

        return TokenResponseDTO(access_token=token, token_type="bearer")