
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from app.db.models.user import User
from app.db.models.device import Device
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.db.session import get_db

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="api/auth/token")
api_key_header=APIKeyHeader(name="X-API-Key",auto_error=False)


def get_current_user(
        token: str =Depends(oauth2_scheme),
        db: Session = Depends(get_db),
)->User:
    
    credentials_exception= HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"},
    )

    payload= decode_access_token(token)
    if payload is None:
        raise credentials_exception
    email: str= payload.get("sub")
    if email is None:
        raise credentials_exception
    user= db.query(User).filter(User.email==email).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    return user

async def get_device_by_api(
        api_key: str=Depends(api_key_header),
        db:Session = Depends(get_db)
)->Device:
    if not api_key:
        raise HTTPException(
        status_code=401,
        detail="X-API-Key header missing"
        )
    device= db.query(Device).filter(
        Device.api_key==api_key,
        Device.is_active==True
    ).first()

    if not device:
        raise HTTPException(
            status_code=401,
            detail="invalid or inactive API Key"
        )
    return device
