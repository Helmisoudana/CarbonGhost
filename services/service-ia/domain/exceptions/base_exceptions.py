"""
Exceptions de base communes à TOUS les services.
Ne pas mettre de logique spécifique à un service ici.
"""


class DomainException(Exception):
    """Exception racine du domaine. Toute exception métier en hérite."""


class NotFoundException(DomainException):
    """Ressource introuvable (-> 404)."""


class ValidationException(DomainException):
    """Donnée invalide (-> 422)."""


class ConflictException(DomainException):
    """Conflit d'état, ex: ressource déjà existante (-> 409)."""


class UnauthorizedException(DomainException):
    """Accès non autorisé (-> 401)."""
