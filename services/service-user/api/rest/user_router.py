from fastapi import APIRouter, Depends, status
# on importe les DTOs pour valider les entrées et sorties des routes
from application.dtos.user_dto import(
    UserCreateDTO,
    UserLoginDTO,
    UserResponseDTO,
    UserTokenDTO,
)
# on importe la classe des use cases pour le typage
from application.use_cases.authenticate_user import AuthenticateUserUseCase
from application.use_cases.get_user_profile import GetUserProfileUseCase
from application.use_cases.register_user import RegisterUserUseCase

# on importe les dépendances pour récupérer les use cases depuis le container
from api.rest.deps import (
    get_authenticate_user_use_case,
    get_get_user_profile_use_case,
    get_register_user_use_case,
)
from container import Container

router = APIRouter(prefix="/user", tags=["user"])

# on définit les routes pour les opérations liées aux utilisateurs
# route pour l'enregistrement d'un nouvel utilisateur(inscription)
@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def register(
    dto: UserCreateDTO,
    use_case: RegisterUserUseCase =Depends(get_register_user_use_case),
):
    return use_case.execute(dto)

@router.post("/login", response_model=UserTokenDTO)
def login(
    dto: UserLoginDTO,
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
):
    return use_case.execute(dto)


@router.get("/{user_id}", response_model=UserResponseDTO)
def get_profile(
    user_id: str,
    use_case: GetUserProfileUseCase = Depends(get_get_user_profile_use_case),
):
    return use_case.execute(user_id)