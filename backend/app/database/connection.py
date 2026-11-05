from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config import DATABASE_URL
from backend.app.database.models import Base

# Engine configuration: Handles both SQLite and Neon PostgreSQL
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Ensure clean driver prefix
db_url = DATABASE_URL
if db_url.startswith("postgresql://") and "psycopg" not in db_url:
    # Use psycopg binary (v3 or v2)
    pass

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables in the configured database (PostgreSQL / SQLite)."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Successfully connected to database and initialized tables.")
    except Exception as e:
        print(f"Warning: Primary database connection error ({e}).")

@contextmanager
def get_db():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db_session():
    """FastAPI Dependency yield."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

