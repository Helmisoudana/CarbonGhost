import os
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Récupère la clé secrète du .env, ou prend une clé de secours en dev
SECRET_KEY = os.getenv("JWT_SECRET", "super_secret_key_carbonghost")
ALGORITHM = "HS256"

# Récupère la durée d'expiration du .env (convertie en entier)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 60))


class JWTService:

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            return None