from fastapi import APIRouter

router = APIRouter(prefix="/mesures", tags=["mesures"])

# TODO: brancher les routes sur les use cases de application/use_cases/
# En cas d'erreur métier, lever une exception de domain/exceptions/base_exceptions.py
# (NotFoundException, ValidationException, ...), le container s'occupe du reste.
