from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str

    model_config = {"from_attributes": True}


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    hashed_password: str


class UserRead(UserBase):
    id: int


class LoginRequest(BaseModel):
    username: str
    password: str
