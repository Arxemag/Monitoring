import asyncio
import aiohttp
from app.database import get_db_session
from app.models import Server, Service

BATCH_SIZE = 100  # Сколько портов одновременно проверяем

async def check_port(session, domain, port):
    url = f"http://{domain}:{port}"
    try:
        async with session.get(url, timeout=3) as response:
            if response.status < 400:
                return port
    except Exception:
        pass
    return None

async def scan_ports_batch(session, domain, ports_batch):
    tasks = [check_port(session, domain, port) for port in ports_batch]
    results = await asyncio.gather(*tasks)
    return [port for port in results if port]

async def scan_server(server: Server):
    open_ports = []
    ports = range(1, 10000)  # Диапазон портов для проверки

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(ports), BATCH_SIZE):
            ports_batch = ports[i:i+BATCH_SIZE]
            found_ports = await scan_ports_batch(session, server.ip_or_domain, ports_batch)
            if found_ports:
                for port in found_ports:
                    print(f"Найден открытый порт: {port}")
                open_ports.extend(found_ports)

    return open_ports

def save_services(server: Server, ports: list, db):
    for port in ports:
        existing = db.query(Service).filter_by(server_id=server.id, port=port).first()
        if not existing:
            service = Service(
                server_id=server.id,
                port=port,
                admin_url=f"http://{server.ip_or_domain}:{port}",
                description="Открытый порт (автоматическое добавление)"
            )
            db.add(service)
    db.commit()
    print(f"Добавлено {len(ports)} сервисов в базу.")

def main():
    with get_db_session() as db:
        server = db.query(Server).filter_by(name="SUNTD").first()
        if not server:
            print("Сервер SUNTD не найден в базе.")
            return

        print(f"Начинаем сканирование сервера {server.name} ({server.ip_or_domain})...")
        open_ports = asyncio.run(scan_server(server))

        if open_ports:
            save_services(server, open_ports, db)
        else:
            print("Открытые порты не найдены.")

if __name__ == "__main__":
    main()