import re
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Server, ServerInfo, CatalogStatus
from app.services.site_parser import SiteParser

def clean_html_tags(text: str) -> str:
    """Удаляет HTML-теги, чтобы корректно искать текст."""
    return re.sub(r"<.*?>", "", text)

# --- Парсер главной страницы админки ---
async def parse_admin_title(text: str, server: Server, port: int, db: Session):
    cleaned_text = clean_html_tags(text)  # <-- Чистим теги перед парсингом!

    reg_number_match = re.search(r"Регистрационный номер:\s*\d+_(\d+)", cleaned_text)
    expiration_date_match = re.search(r"до\s*(\d{2}\.\d{2}\.\d{4})", cleaned_text)
    reg_file_limit_match = re.search(r"Ограничение рег\. файла:\s*(\d+)", cleaned_text)
    session_count_match = re.search(r"Всего соединений \(сессии\):\s*(\d+)", cleaned_text)

    server_info = db.query(ServerInfo).filter(
        ServerInfo.server_id == server.id, ServerInfo.port == port
    ).first()

    if not server_info:
        server_info = ServerInfo(server_id=server.id, port=port)
        db.add(server_info)
        db.commit()

    if reg_number_match:
        server_info.registration_number = int(reg_number_match.group(1))
    if expiration_date_match:
        server_info.expiration_date = datetime.strptime(expiration_date_match.group(1), "%d.%m.%Y").date()
    if reg_file_limit_match:
        server_info.license_limit = int(reg_file_limit_match.group(1))
    if session_count_match:
        server_info.sessions_count = int(session_count_match.group(1))

    db.commit()
    print(f"[INFO] Обновлены данные в server_info для порта {port}")

# --- Парсер настроек резервного копирования ---
async def parse_admin_pref(text: str, server: Server, port: int, db: Session):
    # Новый, более точный парсинг
    backup_time_match = re.search(r"Время, когда производить резервное копирование:\s*([\d]{2}:[\d]{2})", text)
    restart_time_match = re.search(r"Укажите время, когда производить перезапуск сервера\s*([\d]{2}:[\d]{2})", text)

    server_info = db.query(ServerInfo).filter(
        ServerInfo.server_id == server.id, ServerInfo.port == port
    ).first()

    if not server_info:
        server_info = ServerInfo(server_id=server.id, port=port)
        db.add(server_info)

    if backup_time_match:
        server_info.backup_time = backup_time_match.group(1)
    if restart_time_match:
        server_info.restart_time = restart_time_match.group(1)

    db.commit()

    print(f"[INFO] Обновлены настройки резервного копирования для порта {port}")

async def parse_sysinfo_metrics(text: str, server: Server, port: int, db: Session):
    main_page_pattern = re.compile(r'kserver_main_page\{.*?path="([^"]+)"\} (\d+)')
    db_pattern = re.compile(r'kserver_product_control\{.*?path="([^"]+)"\} (\d+)')

    main_page_matches = main_page_pattern.findall(text)
    db_matches = db_pattern.findall(text)

    db.query(CatalogStatus).filter(
        CatalogStatus.server_id == server.id, CatalogStatus.port == port
    ).delete()

    catalog_map = {}

    for path, status in main_page_matches:
        catalog_map.setdefault(path, {})["main_page_status"] = int(status)

    for path, status in db_matches:
        catalog_map.setdefault(path, {})["db_status"] = int(status)

    for path, status_data in catalog_map.items():
        catalog_status = CatalogStatus(
            server_id=server.id,
            port=port,
            path=path,
            main_page_status=status_data.get("main_page_status", 0),
            db_status=status_data.get("db_status", 0)
        )
        db.add(catalog_status)

    db.commit()
    print(f"[INFO] Добавлены записи в catalog_status для порта {port} ({len(catalog_map)} штук)")

async def parse_server_data(server: Server, db: Session):
    ports = [port.strip() for port in server.ports.split(",") if port.strip().isdigit()]

    for port in ports:
        base_url = f"http://{server.ip_or_domain}:{port}"
        parser = SiteParser(base_url)

        try:
            print(f"[INFO] Парсим порт {port} ({base_url})")
            await parser.login()
            text_title = await parser.fetch("/admin/title")
            text_pref = await parser.fetch("/admin/pref")
            text_metrics = await parser.fetch("/sysinfo/metrics")

            await parse_admin_title(text_title, server, int(port), db)
            await parse_admin_pref(text_pref, server, int(port), db)
            await parse_sysinfo_metrics(text_metrics, server, int(port), db)

            print(f"[SUCCESS] Парсинг завершён успешно на {base_url}")

        except Exception as e:
            print(f"[ERROR] Ошибка при парсинге на {base_url}: {e}")
        finally:
            await parser.close()

async def save_admin_links_to_db(db: Session, server_id: int):
    server = db.query(Server).filter(Server.id == server_id).first()
    if server:
        await parse_server_data(server, db)
