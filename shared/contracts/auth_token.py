from pydantic import BaseModel

class AuthTokenPayload(BaseModel):
    user_id: str
    email: str
    role: str
    exp:int