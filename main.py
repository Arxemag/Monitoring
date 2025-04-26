from fastapi import FastAPI
from app.database import init_db, get_db_session_context
from app.api import router as api_router
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Monitoring Service...")
    init_db()
    with get_db_session_context() as db:
        from app.database import seed_servers
        seed_servers(db)
    logger.info("Monitoring Service started successfully ✅")
    yield
    logger.info("Shutting down Monitoring Service...")

app = FastAPI(
    title="Monitoring Service",
    description="Сервис для опроса серверов и парсинга страниц",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Monitoring Service is up and running!"}
