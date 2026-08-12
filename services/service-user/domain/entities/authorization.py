from enum import Enum
from typing import Set

class Permission(str , Enum):

    READ_MACHINES = "machines:read"
    VALIDATE_RECOMMENDED_ACTIONS = "actions:validate"

    READ_CARBON_PAGE = "carbon:read"
    EXPORT_REPORTS = "reports:export"

    MANAGE_USERS = "users:manage"
    MANAGE_CONFIG = "machines_config:manage"
    
    USE_LLM_ASSISTANT = "llm:use"

class UserRole(str , Enum):#PME

    OPERATOR = "OPERATOR"
    LINE_MANAGER = "LINE_MANAGER"
    ENERGY_RSE_MANAGER = "ENERGY_RSE_MANAGER"
    SUPER_ADMIN = "SUPER_ADMIN"#equipe plateforme

    # matrice d'association(quel role posscede quelles permissions)

ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.SUPER_ADMIN: set(Permission),  # tous les droits
    UserRole.LINE_MANAGER: {
        Permission.READ_MACHINES,
        Permission.VALIDATE_RECOMMENDED_ACTIONS,
        Permission.USE_LLM_ASSISTANT,
    },
    UserRole.ENERGY_RSE_MANAGER: {
        Permission.READ_CARBON_PAGE,
        Permission.EXPORT_REPORTS,
        Permission.USE_LLM_ASSISTANT,
    },
    UserRole.OPERATOR: {
        Permission.READ_MACHINES,
        Permission.USE_LLM_ASSISTANT,
    },

}