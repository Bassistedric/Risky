from pydantic import BaseModel


class UserLoginRequest(BaseModel):
    initials: str