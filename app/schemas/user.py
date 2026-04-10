from pydantic import BaseModel,EmailStr

class UserBase(BaseModel):
    email:EmailStr
    full_name:str

class UserRegister(UserBase):

    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    model_config = {"from_attributes": True}

class TokenData(BaseModel):
    email:str |None = None 

class Token(BaseModel):
    access_token: str
    token_type: str