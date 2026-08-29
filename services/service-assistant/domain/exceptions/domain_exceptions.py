class DomainException(Exception):
    """Exception générale du domaine."""
    pass


class UnsafeQuestionException(DomainException):
    """Question refusée par la politique de sécurité."""
    pass


class UnsafeResponseException(DomainException):
    """Réponse du LLM refusée par la politique de sécurité."""
    pass


class EventNotFoundException(DomainException):
    """Aucun événement trouvé."""
    pass