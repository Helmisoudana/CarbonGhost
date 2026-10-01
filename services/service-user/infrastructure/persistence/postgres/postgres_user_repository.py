# le role de cette class est de faire le lien entre la base de données (PostgreSQL) et le domaine (via l'ORM SQLAIchemy)

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities.user import User
from infrastructure.persistence.postgres.models import UserModel
from domain.ports.repositories.repository import IUserRepository

class PostgresUserRepository(IUserRepository):
    """Implementation of IUserRepository using PostgreSQL and SQLAlchemy"""
    def __init__(self, session: Session):
        self.session = session

    "create a new user in the database"
    def save(self, user: User) -> None:
        model = UserModel(
            id = user.id,
            username = user.username,
            email = user.email,
        password = user.password,
        role = user.role,
        badge_id = user.badge_id,
        created_at = user.created_at,
    )# convertir l'entité User en modèle SQLAlchemy
        self.session.add(model)
        self.session.commit()

    def find_by_id(self, user_id: str) -> User| None:
        model = self.session.get(UserModel, user_id)
        return self.to_entity(model) if model else None

    def find_by_email(self, email: str) -> User| None:
        stmt = select(UserModel).where(UserModel.email == email)# requête SQL pour trouver un utilisateur par email(statement)
        model = self.session.scalars(stmt).first()# exécuter la requête et récupérer le premier résultat
        return self.to_entity(model) if model else None

    def to_entity(self, model: UserModel) -> User:# convertir un modèle SQLAlchemy en entité User
        return User(
    
        id = model.id,
        username = model.username,
        email = model.email,
        password = model.password,
        role = model.role,
        badge_id = model.badge_id,
        created_at = model.created_at,
    )