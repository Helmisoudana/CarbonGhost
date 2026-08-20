from sqlalchemy.orm import Session

# Adapters (Infrastructure Layer)
from infrastructure.persistence.postgres.postgres_user_repository import PostgresUserRepository
from infrastructure.security.bcrypt_service import BcryptService
from infrastructure.security.jwt_service import JWTService

# use_cases (Application Layer)
from application.use_cases.register_user import RegisterUserUseCase
from application.use_cases.authenticate_user import AuthenticateUserUseCase
from application.use_cases.get_user_profile import GetUserProfileUseCase

class Container:
    """Dependency Injection Container for the User Service."""
    def __init__(self, db_session: Session):
        #  Adapters (Infrastructure Layer)
        self.user_repository = PostgresUserRepository(db_session)
        self.hashing_service = BcryptService()
        self.token_service = JWTService()
        # Use Cases (Application Layer)
        self.register_user_use_case = RegisterUserUseCase(
            user_repository=self.user_repository,
            hashing_service=self.hashing_service
        )
        self.authenticate_user_use_case = AuthenticateUserUseCase(
            user_repository=self.user_repository, # inject the user repository dependency
            hashing_service=self.hashing_service, 
            token_service=self.token_service
        )
        self.get_user_profile_use_case = GetUserProfileUseCase(
            user_repository=self.user_repository
        )

