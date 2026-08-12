class DomainException(Exception):
    """Exception racine du domaine. Toute exception métier en hérite."""
    pass


class UserNotFoundException(DomainException):
    """user introuvable (-> 404)."""
    def __init__(self, msg: str= "user not found"):
        super().__init__(msg)


class UserAlreadyExistsException(DomainException):
    """when an email or badged_id already exists in the database (-> 409)."""
    def __init__(self, msg: str= "user already exists"):
        super().__init__(msg)


class AuthenticationFailedException(DomainException):
    """invalid credentials (-> 401)."""
    def __init__(self, msg: str= "invalid credentials"):
        super().__init__(msg)

class UserInactiveException(DomainException):
    """user is inactive and cannot perform actions (-> 403)."""
    def __init__(self, msg: str= "User account is inactive"):
        super().__init__(msg)
