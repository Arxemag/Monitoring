from fastapi import FastAPI
from app.database import init_db, get_db_session_context, seed_servers
from app.api import router as api_router
from app.api_services import router as services_router
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import logging

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Жизненный цикл приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Monitoring Service...")

    # Инициализация базы данных
    init_db()
    logger.info("Database initialized ✅")

    # Первичная загрузка серверов
    with get_db_session_context() as db:
        seed_servers(db)
    logger.info("Servers seeded ✅")

    yield
    logger.info("Shutting down Monitoring Service...")

# Создание приложения
app = FastAPI(
    title="Monitoring Service",
    description="Сервис для мониторинга серверов и парсинга страниц",
    version="0.1.0",
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Указывай фронт — так безопаснее
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(api_router, prefix="/api")
app.include_router(services_router, prefix="/api")

# Тестовый маршрут
@app.get("/")
def read_root():
    return {"message": "Monitoring Service is up and running!"}
