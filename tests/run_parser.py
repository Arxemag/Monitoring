import asyncio
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from app.database import SessionLocal
from app.models import Server
from app.parser import parse_server_data

console = Console()

async def test_parsing():
    db = SessionLocal()

    servers = db.query(Server).filter(Server.ports.in_([1212, 1210])).all()
    if not servers:
        console.print("[bold red]❌ Сервера с нужными портами не найдены[/]")
        return

    console.print(f"[bold cyan]🔍 Найдено {len(servers)} серверов для парсинга[/]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Старт парсинга...", total=len(servers))

        for server in servers:
            try:
                progress.update(task, description=f"Парсим {server.host}:{server.ports}...")
                await parse_server_data(server, db)
                console.print(f"[green]✅ Парсинг завершен:[/] {server.host}:{server.ports}")
            except Exception as e:
                console.print(f"[red]⚠️ Ошибка при парсинге {server.host}:{server.ports}: {e}[/]")
            finally:
                progress.advance(task)

    db.close()
    console.print("[bold green]🎉 Все сервера обработаны![/]")

if __name__ == "__main__":
    asyncio.run(test_parsing())
