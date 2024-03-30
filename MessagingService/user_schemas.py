from pydantic import BaseModel, EmailStr


class Service(BaseModel):
    title: str


class UserBase(BaseModel):
    email: EmailStr


class User(UserBase):
    id: int
    connected_services: list[Service]
