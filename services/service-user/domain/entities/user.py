from dataclasses import dataclass, field # dataclass genere auto le const __init__
from typing import Optional, Set
from datetime import datetime, timezone
from .authorization import UserRole, Permission, ROLE_PERMISSIONS

@dataclass

class User:
    # entité metier representant user
    username: str
    email: str
    hashed_password: str

    # attributs indus
    role: UserRole = field(default=UserRole.OPERATOR) # par defaut un user est un operateur
    badge_id: Optional[str] = field(default=None) # badge id pour les operateurs

    id: Optional[str] = None # id de l'utilisateur dans la base de données(clé primaire)

    is_active: bool = field(default=True)#status de compte
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def desactivate(self) -> bool: # si un ouvrier quite l'usine
        self.is_active = False
        return self.is_active

    def activate(self) -> bool:
        self.is_active = True
        return self.is_active
#recuperer l'ensemble des permissions associées au role de cet utilisateur
    def get_permissions(self) -> Set[Permission]:
        return ROLE_PERMISSIONS.get(self.role, set())

    def has_permission(self, permission: Permission) -> bool:#verifier si l'utilisateur posscede une permission specifique
        if not self.is_active:
            return False
        return permission in self.get_permissions()


