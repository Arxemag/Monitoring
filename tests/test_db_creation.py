import os
import pytest
from sqlalchemy import inspect
from app.database import init_db, engine

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Удаляем старую базу данных, если она есть
    if os.path.exists("./monitoring.db"):
        os.remove("./monitoring.db")
    # Инициализируем новую базу данных с таблицами
    init_db()

def test_servers_table_exists():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "servers" in tables, "Таблица 'servers' не создана!"

def test_servers_table_columns():
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("servers")}
    expected_columns = {"id", "name", "ip_or_domain", "ports", "is_active", "meta_info"}
    assert expected_columns.issubset(columns), "Не все ожидаемые колонки найдены в таблице 'servers'!"
