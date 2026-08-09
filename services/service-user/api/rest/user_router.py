from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["user"])

@router("/login")
def login (email, mdp):
    user =login(email, mdp)
    return user 
