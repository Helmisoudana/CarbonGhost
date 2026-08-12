from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from domain.entities.user import UserRole

class CreateUserCommand(BaseModel):
    """DTO pour la création d'un utilisateur.
    DTO d'entrée : Données envoyées par le client pour créer un compte.
    Pydantic valide automatiquement l'email, la longueur des champs, etc."""

    username: str = Field(
        ..., 
        description="Nom d'utilisateur"
        )
    email: EmailStr = Field(
        ..., 
        description="Adresse email de l'utilisateur"
        )
    password: str = Field(
        ..., 
        min_length=8,
        description="Mot de passe de l'utilisateur(au moins 8 caractères)"
        )
    role: UserRole = Field(
        default=UserRole.OPERATOR,
        description="Rôle de l'utilisateur (par défaut: OPERATOR)"
          )
    badge_id: str | None = Field(None, description="ID du badge pour les opérateurs (optionnel)")

class UserResponseDTO(BaseModel):
    """DTO de réponse pour un utilisateur.
    DTO de sortie : Données renvoyées au client après la création ou la récupération d'un utilisateur."""

    id: str = Field(..., description="ID unique de l'utilisateur")
    username: str = Field(..., description="Nom d'utilisateur")
    email: EmailStr = Field(..., description="Adresse email de l'utilisateur")
    role: UserRole = Field(..., description="Rôle de l'utilisateur")
    badge_id: str | None = Field(None, description="ID du badge pour les opérateurs (optionnel)")
    is_active: bool = Field(..., description="Statut actif/inactif de l'utilisateur")
    created_at: datetime = Field(..., description="Date et heure de création du compte (UTC)")

    model_config = {"from_attributes": True}