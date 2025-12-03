"""
SQLAlchemy models package.
Exports all models and database utilities.
"""
from models.database import Base, engine, get_db, SessionLocal
from models.user import User
from models.profile import Profile
from models.note import Note
from models.log import Log


def init_db():
    """
    Create all database tables.
    This should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)
    print(f"Database tables created successfully at: {engine.url}")


__all__ = [
    "Base",
    "engine",
    "get_db",
    "SessionLocal",
    "init_db",
    "User",
    "Profile",
    "Note",
    "Log",
]
