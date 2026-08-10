from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["user"])

<<<<<<< HEAD
# TODO: brancher les routes sur les use cases de application/use_cases/
# En cas d'erreur métier, lever une exception de domain/exceptions/exception.py
# (NotFoundException, ValidationException, ...), le container s'occupe du reste.
=======
@router("/login")
def login (email, mdp):
    user =login(email, mdp)
    return user 
>>>>>>> master
