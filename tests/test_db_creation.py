import os
import pytest
from sqlalchemy import inspect
from app.database import engine
from app.models.base import Base

DB_PATH = os.path.abspath("monitoring.db")  # Делаем абсолютный путь

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_database():
    """Инициализация базы данных перед тестами и удаление после."""
    # Закрываем все подключения к базе
    engine.dispose()

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # После удаления — пересоздаём все таблицы
    Base.metadata.create_all(bind=engine)

    yield

    # После тестов — ещё раз закрыть соединение
    engine.dispose()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_servers_table_exists():
    """Проверяем, что таблица 'servers' создана."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "servers" in tables, f"Таблицы 'servers' нет! Существующие таблицы: {tables}"

def test_servers_table_columns():
    """Проверяем наличие нужных колонок в таблице 'servers'."""
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("servers")}
    expected_columns = {
        "id",
        "name",
        "host",
        "ports",
    }
    assert expected_columns.issubset(columns), f"Не все ожидаемые поля найдены: {columns}"
