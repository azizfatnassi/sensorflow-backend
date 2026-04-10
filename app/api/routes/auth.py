from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.schemas.user import UserRegister,UserResponse,Token
from app.services.auth_service import (get_user_by_email,create_user,authenticate_user,generate_token,)
from app.db.models.user import User



router =APIRouter(prefix="/api/auth",tags=["Authentication"])

@router.post("/register",response_model=UserResponse,status_code=201)
def register(user_data:UserRegister,db:Session=Depends(get_db)):
    existing= get_user_by_email(db,user_data.email)  
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Email already exists")
      
    return create_user(db,user_data)


@router.post("/token",response_model= Token)
def login(form_data: OAuth2PasswordRequestForm =Depends(),
          db:Session=Depends(get_db)):
    user=authenticate_user(db,form_data.username,form_data.password)
    if not user:
        raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Invalid credentials",
             headers={"WWW-Authenticate":"Bearer"},
        )
    return generate_token(user)
    

@router.get("/me",response_model=UserResponse)
def get_me(current_user:User=Depends(get_current_user)):
    return current_user