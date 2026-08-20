from fastapi import Depends
from sqlalchemy.orm import Session

from infrastructure.database import get_db
from container import Container


def get_container(db: Session = Depends(get_db)) -> Container:
    """Fournit une instance de Container injectée avec la session BDD courante."""
    return Container(db_session=db)

# Raccourcis pour chaque Use Case
def get_register_user_use_case(container: Container = Depends(get_container)):
    return container.register_user_use_case()


def get_authenticate_user_use_case(
    container: Container = Depends(get_container),
):
    return container.authenticate_user_use_case()


def get_get_user_profile_use_case(
    container: Container = Depends(get_container),
):
    return container.get_user_profile_use_case()