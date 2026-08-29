from domain.exceptions.domain_exceptions import UnsafeQuestionException, UnsafeResponseException


class SafetyPolicy:
    FORBIDDEN_PATTERNS = [
        "password",
        "mot de passe",
        "api key",
        "clé api",
        "secret",
        "token",
        "hack",
        "pirate",
        "sql injection",
        "injection sql",
    ]

    FORBIDDEN_RESPONSE_PATTERNS = [
        "arrête la machine",
        "stop la machine",
        "désactive",
        "shutdown",
        "certificat",
        "mot de passe",
        "clé api",
        "token",
    ]

    @classmethod
    def validate_question(cls, question: str) -> None:
        normalized_question = question.lower().strip()
        if not normalized_question:
            raise UnsafeQuestionException("La question ne peut pas être vide.")
        for pattern in cls.FORBIDDEN_PATTERNS:
            if pattern in normalized_question:
                raise UnsafeQuestionException("Cette demande n'est pas autorisée.")
        if len(question) > 2000:
            raise UnsafeQuestionException("La question est trop longue.")

    @classmethod
    def validate_response(cls, response: str) -> None:
        normalized_response = response.lower()
        for pattern in cls.FORBIDDEN_RESPONSE_PATTERNS:
            if pattern in normalized_response:
                raise UnsafeResponseException("Cette réponse a été bloquée par la politique de sécurité.")