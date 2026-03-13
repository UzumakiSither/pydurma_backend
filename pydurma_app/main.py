"""
FastAPI application entrypoint.

Includes:
- Router registration
- Startup tasks (schema creation + optional seeding)
"""

from fastapi import FastAPI

from pydurma_app.routers.auth_router import router as auth_router
from pydurma_app.routers.collate_router import router as collate_router
from pydurma_app.db.database import Base, engine
from pydurma_app.db.seed import seed_users
from pydurma_app.db.database import SessionLocal
from pydurma_app.config import get_settings

app = FastAPI(title="Pydurma API", description="API for Pydurma")

app.include_router(auth_router)
app.include_router(collate_router)


@app.on_event("startup")
def on_startup():
    """Initialize database schema and optionally seed local users."""
    try:
        is_local  = get_settings().env_name == "Local"
        if is_local:
            Base.metadata.drop_all(bind=engine)

        Base.metadata.create_all(bind=engine)
        
        if is_local:
            print("Seeding users")
            db = SessionLocal()
            try:
                seed_users(db)
            except Exception as e:
                print(f"Seeding failed: {e}")
            finally:
                db.close() 
    except Exception as e:
        print(e)

@app.get("/")
def root():
    return {"message": "Welcome to the Pydurma API"}

