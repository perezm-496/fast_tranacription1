from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from elise.utils.auth import decode_access_token
from elise.models import TokenData
from jose import JWTError
from elise.database import db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/elise/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.users.find_one({"email": email})
    if not user:
        raise credentials_exception
    return user
