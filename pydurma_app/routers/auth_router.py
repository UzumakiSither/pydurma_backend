"""
Authentication endpoints.

- `POST /auth/register`: register a new user
- `POST /auth/login`: login and receive a JWT access token
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from pydurma_app.db.database import get_db
from pydurma_app.schemas.schema import UserRegister, UserLogin, TokenResponse
from pydurma_app.services.auth_service import register_user, login_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    register_user(db, user.username, user.email, user.password)

    return {"message": "User registered"}


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login and return a JWT access token."""
    token = login_user(db, user.username, user.password)

    return {"access_token": token}