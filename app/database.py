import os
import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# --- ИНИЦИАЛИЗАЦИЯ БАЗЫ: создание таблиц
def init_db():
    from app import models

    db_exists = os.path.exists("./monitoring.db")

    Base.metadata.create_all(bind=engine)

    if not db_exists:
        logger.info("Создан новый файл базы данных monitoring.db 🛠️")
    else:
        logger.info("Файл базы данных уже существовал, проверка таблиц ✅")

    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "servers" in tables:
        logger.info("Таблица 'servers' готова ✅")
    else:
        logger.error("Таблица 'servers' не найдена после инициализации! ❌")

# --- ЗАСЕИВАНИЕ БАЗЫ ДАННЫМИ
def seed_servers(db: Session):
    from app.models import Server

    existing_server = db.query(Server).filter_by(name="SUNTD").first()
    if existing_server:
        logger.info("Сервер 'SUNTD' уже существует в базе данных. Пропускаем добавление ✅")
        return

    suntd_server = Server(
        name="SUNTD",
        ip_or_domain="suntd.kodeks.expert",
        ports="",
        is_active=True,
        meta_info="Initial SUNTD server",
    )
    db.add(suntd_server)
    db.commit()
    logger.info("Добавлен сервер 'SUNTD' в базу данных 📦")
