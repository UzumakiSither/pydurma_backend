"""Authentication dependencies (JWT validation)."""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from dataclasses import dataclass

from pydurma_app.core.security import SECRET_KEY, ALGORITHM

bearer_scheme = HTTPBearer()

@dataclass
class TokenUser:
    id: int

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        ) -> TokenUser:
    """Validate JWT and return user data from token."""

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    return TokenUser(id=int(user_id))
