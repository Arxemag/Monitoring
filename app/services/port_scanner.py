import asyncio
import socket
from app.database import get_db_session
from app.models import Server

BATCH_SIZE = 50  # Размер пакета портов для параллельной проверки

def generate_ports():
    """Генерация списка портов по заданной маске."""
    ports = {80, 1000, 1010, 1210, 1212}
    for base in range(2000, 10000, 1000):
        ports.add(base)
        ports.add(base + 20)
        ports.add(base + 30)
    return sorted(ports)

async def check_port(host: str, port: int, timeout: float = 1.0) -> int | None:
    """Асинхронная проверка одного порта."""
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
    """Проверка группы портов."""
    tasks = [check_port(host, port) for port in ports_batch]
    results = await asyncio.gather(*tasks)
    return [port for port in results if port is not None]

async def scan_server_ports(server: Server) -> list[int]:
    """Сканирование портов для конкретного сервера."""
    open_ports = []
    ports = generate_ports()

    for i in range(0, len(ports), BATCH_SIZE):
        ports_batch = ports[i:i + BATCH_SIZE]
        found_ports = await scan_ports_batch(server.ip_or_domain, ports_batch)
        if found_ports:
            for port in found_ports:
                print(f"Найден открытый порт: {port}")
            open_ports.extend(found_ports)

    return open_ports

def save_ports_to_server(server: Server, ports: list[int], db):
    """Сохранение открытых портов обратно в базу."""
    server.ports = ",".join(map(str, ports))
    db.add(server)  # не забудь добавить обратно в сессию
    db.commit()
    print(f"Обновлены открытые порты у сервера {server.name}: {server.ports}")

def main():
    """Основная функция для запуска сканирования."""
    with get_db_session() as db:
        server = db.query(Server).filter_by(name="SUNTD").first()
        if not server:
            print("Сервер 'SUNTD' не найден в базе.")
            return

        print(f"Начинаем сканирование сервера {server.name} ({server.ip_or_domain})...")
        open_ports = asyncio.run(scan_server_ports(server))

        if open_ports:
            save_ports_to_server(server, open_ports, db)
        else:
            print("Открытые порты не найдены.")

if __name__ == "__main__":
    main()
