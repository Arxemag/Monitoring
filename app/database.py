
import os
import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# --- Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Настройки базы данных
DATABASE_URL = "sqlite:///./monitoring.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Базовая модель
from app.models.base import Base

# --- Сессия для обычного использования через `with`
@contextmanager
def get_db_session_context():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка в сессии БД: {e}")
        raise
    finally:
        db.close()

# --- Сессия для использования в FastAPI Depends
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Инициализация базы данных: создание таблиц
def init_db():
    from app.models import Server, ServerInfo, CatalogStatus, Service

    db_existed = os.path.exists("./monitoring.db")

    Base.metadata.create_all(bind=engine)

    if db_existed:
        logger.info("Файл базы данных уже существовал ✅")
    else:
        logger.info("Создан новый файл базы данных monitoring.db 🛠️")

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if "servers" in tables:
        logger.info("Таблица 'servers' готова ✅")
    else:
        logger.error("Таблица 'servers' не найдена после инициализации! ❌")

# --- Засеивание базы начальными данными
def seed_servers(db: Session):
    from app.models.server import Server

    try:
        existing_server = db.query(Server).filter_by(name="SUNTD").first()
        if existing_server:
            logger.info("Сервер 'SUNTD' уже существует в базе данных. Пропускаем добавление ✅")
            return

        suntd_server = Server(
            name="SUNTD",
            ip_or_domain="suntd.kodeks.expert",
            ports=""
        )
        db.add(suntd_server)
        db.commit()
        logger.info("Добавлен сервер 'SUNTD' в базу данных 📦")
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при засевании сервера 'SUNTD': {e}")
        raise
