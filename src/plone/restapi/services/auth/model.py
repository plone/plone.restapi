from pydantic import BaseModel


class LoginData(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    token: str


class ErrorResponse(BaseModel):
    error: dict
