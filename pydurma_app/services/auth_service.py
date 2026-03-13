from sqlalchemy.orm import Session
from fastapi import HTTPException

from pydurma_app.models.User import User
from pydurma_app.core.security import hash_password, verify_password, create_access_token


def register_user(db: Session, username: str, email: str, password: str):

    existing = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(db: Session, username: str, password: str):

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return create_access_token(user.id)