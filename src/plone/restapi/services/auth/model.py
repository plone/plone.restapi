from pydantic import BaseModel


class LoginInputDTO(BaseModel):
    login: str
    password: str


class TokenOutputDTO(BaseModel):
    token: str
