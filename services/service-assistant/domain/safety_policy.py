from domain.exceptions.domain_exceptions import UnsafeQuestionException


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

    @classmethod
    def validate_question(cls, question: str) -> None:

        normalized_question = question.lower().strip()

        if not normalized_question:
            raise UnsafeQuestionException(
                "La question ne peut pas être vide."
            )

        for pattern in cls.FORBIDDEN_PATTERNS:
            if pattern in normalized_question:
                raise UnsafeQuestionException(
                    "Cette demande n'est pas autorisée."
                )

        if len(question) > 2000:
            raise UnsafeQuestionException(
                "La question est trop longue."
            )