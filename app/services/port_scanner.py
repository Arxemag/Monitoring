import asyncio
import socket
from app.models import Server
from app.database import SessionLocal

BATCH_SIZE = 50

def generate_ports():
    ports = {80, 1000, 1010, 1210, 1212}
    for base in range(2000, 10000, 1000):
        ports.add(base)
        ports.add(base + 20)
        ports.add(base + 30)
    return sorted(ports)

async def check_port(host: str, port: int, timeout: float = 1.0) -> int | None:
    loop = asyncio.get_running_loop()
    try:
        await asyncio.wait_for(
            loop.run_in_executor(None, lambda: socket.create_connection((host, port), timeout)),
            timeout
        )
        return port
    except Exception:
        return None

async def scan_ports_batch(host: str, ports_batch: list[int]) -> list[int]:
    tasks = [check_port(host, port) for port in ports_batch]
    results = await asyncio.gather(*tasks)
    return [port for port in results if port is not None]

async def scan_server_ports(server: Server, db) -> list[int]:
    open_ports = []
    ports = generate_ports()

    for i in range(0, len(ports), BATCH_SIZE):
        ports_batch = ports[i:i + BATCH_SIZE]
        found_ports = await scan_ports_batch(server.ip_or_domain, ports_batch)
        if found_ports:
            for port in found_ports:
                print(f"Найден открытый порт: {port}")
            open_ports.extend(found_ports)

    if open_ports:
        server.ports = ",".join(str(port) for port in sorted(open_ports))
        db.add(server)
        db.commit()
        print(f"[SUCCESS] Порты сохранены в сервер: {server.ports}")
    else:
        print("[INFO] Открытые порты не найдены.")

    return open_ports