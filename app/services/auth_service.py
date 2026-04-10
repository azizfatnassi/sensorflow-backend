
from app.db.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user import UserRegister
from app.core.security import hash_password,verify_password, create_access_token


def get_user_by_email(db:Session,email: str) ->User | None:
    return db.query(User).filter(User.email==email).first()
def create_user(db:Session, user_data:UserRegister)->User:
    hashed=hash_password(user_data.password)
    db_user=User(email=user_data.email,hashed_password=hashed,full_name=user_data.full_name)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db:Session,email:str,password:str)->User | None :
    user= get_user_by_email(db,email)
    if not user:
        return None
    if not verify_password(password,user.hashed_password):
        return None
    return user

def generate_token(user:User)->dict:
    token = create_access_token(data={"sub":user.email})
    return {"access_token":token,"token_type":"bearer"}