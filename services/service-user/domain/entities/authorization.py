from enum import Enum
from typing import Set

class Permission(str , Enum):

    READ_MACHINE_DASHBOARD = "machine:read"
    READ_MULTI_MACHINES = "multi_machines:read"
    VALIDATE_RECOMMENDED_ACTIONS = "actions:validate"

    READ_CARBON_PAGE = "carbon:read"
    EXPORT_REPORTS = "reports:export"
    COMPARE_PERFORMANCE = "analytics:compare"    

    MANAGE_USERS = "users:manage"
    MANAGE_THRESHOLDS = "thresholds:manage"#Le droit de régler la sensibilité des alarmes et les limites physiques des capteurs
    MANAGE_CARBON_FACTORS = "carbon_factors:manage"
    MANAGE_MACHINES_CONFIG = "machines_config:manage"
    
    USE_LLM_ASSISTANT = "llm:use"

class UserRole(str , Enum):#PME

    OPERATOR = "OPERATOR"
    LINE_MANAGER = "LINE_MANAGER"
    ENERGY_RSE_MANAGER = "ENERGY_RSE_MANAGER"
    SUPER_ADMIN = "SUPER_ADMIN"#equipe plateforme
    TECH_ADMIN = "TECH_ADMIN"#admin technique de l'usine
    AUDITOR = "AUDITOR" # son role est de vérifier que les données sont correctes et que les actions sont conformes aux normes et aux réglementations. Il peut être un auditeur interne ou externe, selon le contexte de l'entreprise.

    # matrice d'association(quel role posscede quelles permissions)

ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.SUPER_ADMIN: set(Permission),  # tous les droits
    UserRole.TECH_ADMIN: {
        Permission.READ_MACHINE_DASHBOARD,
        Permission.READ_MULTI_MACHINES,
        Permission.MANAGE_USERS,
        Permission.MANAGE_THRESHOLDS,
        Permission.MANAGE_CARBON_FACTORS,
        Permission.MANAGE_MACHINES_CONFIG,
        Permission.USE_LLM_ASSISTANT,
    },
    UserRole.LINE_MANAGER: {
        Permission.READ_MACHINE_DASHBOARD,
        Permission.READ_MULTI_MACHINES,
        Permission.VALIDATE_RECOMMENDED_ACTIONS,
        Permission.USE_LLM_ASSISTANT,
    },
    UserRole.ENERGY_RSE_MANAGER: {
        Permission.READ_CARBON_PAGE,
        Permission.EXPORT_REPORTS,
        Permission.COMPARE_PERFORMANCE,
        Permission.USE_LLM_ASSISTANT,
    },
    UserRole.OPERATOR: {
        Permission.READ_MACHINE_DASHBOARD,
        Permission.USE_LLM_ASSISTANT,
    },

    UserRole.AUDITOR: {
        Permission.READ_MACHINE_DASHBOARD,
        Permission.READ_MULTI_MACHINES,
        Permission.READ_CARBON_PAGE,
        Permission.COMPARE_PERFORMANCE,
    },
}