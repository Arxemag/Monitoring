from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from contextlib import contextmanager

Base = declarative_base()

DATABASE_URL = "sqlite:///./monitoring.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- для обычного использования через `with`
@contextmanager
def get_db_session_context():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# --- для Depends в FastAPI
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app import models
    Base.metadata.create_all(bind=engine)

def seed_servers(db: Session):
    from app.models import Server

    if not db.query(Server).filter_by(name="SUNTD").first():
        suntd_server = Server(
            name="SUNTD",
            ip_or_domain="suntd.kodeks.expert",
            ports="",
            is_active=True,
            meta_info="Initial SUNTD server",
        )
        db.add(suntd_server)
        db.commit()
