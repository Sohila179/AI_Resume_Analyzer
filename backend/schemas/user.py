from pydantic import BaseModel, Field,ConfigDict
from pydantic.networks import EmailStr



class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    username: str = Field(..., example="John Doe")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="securepassword")


class UserUpdate(UserBase):
    password: str = Field(None, min_length=8, example="newpassword")


class UserResponse(UserBase):
    id: int = Field(..., example=1)

    model_config = ConfigDict(from_attributes=True)

class userLogin(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8, example="securepassword")
    