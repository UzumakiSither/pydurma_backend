from sqlalchemy.orm import Session

from pydurma_app.db.database import Base, engine
from pydurma_app.models.User import User
from pydurma_app.core.security import hash_password


def seed_users(db: Session):

    existing_user = db.query(User).filter(
        User.username == "admin"
    ).first()

    if existing_user:
        return

    admin = User(
        username="admin",
        email="admin@test.com",
        password_hash=hash_password("admin123")
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    print("Seeded default admin user")