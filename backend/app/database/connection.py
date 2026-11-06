from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.config import DATABASE_URL, BACKEND_DIR
from backend.app.database.models import Base

def _init_engine_and_session():
    connect_args = {}
    db_url = DATABASE_URL

    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    eng = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)

    # Test if remote PostgreSQL is accessible; fallback to SQLite if offline/blocked
    if not db_url.startswith("sqlite"):
        try:
            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Successfully connected to Neon Cloud PostgreSQL.")
        except Exception as err:
            print(f"Notice: Neon Cloud DB unreachable ({err}). Falling back to local SQLite.")
            sqlite_file = BACKEND_DIR / "data" / "alpr.db"
            sqlite_file.parent.mkdir(parents=True, exist_ok=True)
            sqlite_url = f"sqlite:///{sqlite_file}"
            eng = create_engine(sqlite_url, connect_args={"check_same_thread": False})
            Base.metadata.create_all(bind=eng)

    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    return eng, session_factory

engine, SessionLocal = _init_engine_and_session()

def init_db():
    """Create all tables and ensure columns exist in configured database."""
    global engine, SessionLocal
    try:
        Base.metadata.create_all(bind=engine)
        # Ensure is_hsrp and hsrp_status exist without breaking existing schemas
        with engine.connect() as conn:
            for col, col_def in [
                ("is_hsrp", "BOOLEAN DEFAULT FALSE"),
                ("hsrp_status", "VARCHAR(64) DEFAULT 'Standard Non-HSRP'")
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE plate_records ADD COLUMN {col} {col_def};"))
                    conn.commit()
                except Exception:
                    pass
        print("Database schema verified and tables ready.")
    except Exception as e:
        print(f"Database schema verification notice: {e}")

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
