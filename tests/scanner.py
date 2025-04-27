import asyncio
import httpx
from sqlalchemy.orm import Session
from app.models import Server

# Проверка одного порта
async def check_port(ip_or_domain: str, port: int) -> bool:
    url = f"http://{ip_or_domain}:{port}"
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            response = await client.get(url)
            return response.status_code != 404
    except (httpx.RequestError, httpx.ConnectTimeout):
        return False

# Сканирование всех портов у сервера
async def scan_server_ports(db: Session, server: Server):
    ports_to_check = range(1, 10000)  # Проверяем порты от 1 до 9999
    open_ports = []

    # Ограничим количество одновременных запросов (чтобы не уложить машину)
    semaphore = asyncio.Semaphore(100)

    async def check_with_semaphore(port):
        async with semaphore:
            if await check_port(server.ip_or_domain, port):
                open_ports.append(port)

    tasks = [check_with_semaphore(port) for port in ports_to_check]
    await asyncio.gather(*tasks)

    # Сохраняем в базу
    server.ports = ",".join(map(str, sorted(open_ports)))
    db.add(server)
    db.commit()
