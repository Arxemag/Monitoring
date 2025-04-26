import re
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Server, ServerInfo, CatalogStatus
from app.services.site_parser import SiteParser
from app.database import SessionLocal

# --- Парсер главной страницы админки ---
async def parse_admin_title(text: str, server: Server, db: Session):
    reg_number_match = re.search(r"Регистрационный номер:\s*\d+_(\d+)", text)
    expiration_date_match = re.search(r"Ограничение по сроку работы системы: до (\d{2}\.\d{2}\.\d{4})", text)
    reg_file_limit_match = re.search(r"Ограничение рег\. файла:\s*(\d+)", text)
    session_count_match = re.search(r"Всего соединений \(сессии\):\s*(\d+)", text)

    server_info = db.query(ServerInfo).filter(ServerInfo.server_id == server.id).first()
    if not server_info:
        server_info = ServerInfo(server_id=server.id)
        db.add(server_info)

    if reg_number_match:
        server_info.registration_number = int(reg_number_match.group(1))
    if expiration_date_match:
        server_info.expiration_date = datetime.strptime(expiration_date_match.group(1), "%d.%m.%Y").date()
    if reg_file_limit_match:
        server_info.license_limit = int(reg_file_limit_match.group(1))
    if session_count_match:
        server_info.sessions_count = int(session_count_match.group(1))

    db.commit()

# --- Парсер настроек лицензий ---
async def parse_admin_lic(text: str, server: Server, db: Session):
    # Пока пропущено — допишем при необходимости
    pass

# --- Парсер настроек резервного копирования и перезапуска ---
async def parse_admin_pref(text: str, server: Server, db: Session):
    backup_time_match = re.search(r"Время, когда производить резервное копирование:\s*([\d:]+)", text)
    restart_time_match = re.search(r"Укажите время, когда производить перезапуск сервера\s*([\d:]+)", text)

    server_info = db.query(ServerInfo).filter(ServerInfo.server_id == server.id).first()
    if not server_info:
        server_info = ServerInfo(server_id=server.id)
        db.add(server_info)

    if backup_time_match:
        server_info.backup_time = backup_time_match.group(1)
    if restart_time_match:
        server_info.restart_time = restart_time_match.group(1)

    db.commit()

# --- Парсер статусов каталогов ---
async def parse_sysinfo_metrics(text: str, server: Server, db: Session):
    main_page_pattern = re.compile(r'kserver_main_page\{.*?path="([^"]+)"\} (\d+)')
    db_pattern = re.compile(r'kserver_product_control\{.*?path="([^"]+)"\} (\d+)')

    main_page_matches = main_page_pattern.findall(text)
    db_matches = db_pattern.findall(text)

    catalog_map = {}

    for path, status in main_page_matches:
        catalog_map.setdefault(path, {})["main_page_status"] = int(status)

    for path, status in db_matches:
        catalog_map.setdefault(path, {})["db_status"] = int(status)

    db.query(CatalogStatus).filter(CatalogStatus.server_id == server.id).delete()

    for path, status_data in catalog_map.items():
        catalog_status = CatalogStatus(
            server_id=server.id,
            path=path,
            main_page_status=status_data.get("main_page_status", 0),
            db_status=status_data.get("db_status", 0)
        )
        db.add(catalog_status)

    db.commit()

# --- Главный метод ---
async def parse_server_data(server: Server, db: Session):
    base_url = f"http://{server.host}:{server.ports}"
    parser = SiteParser(base_url)

    try:
        await parser.login()
        text_title = await parser.fetch("/admin/title")
        text_pref = await parser.fetch("/admin/pref")
        text_metrics = await parser.fetch("/sysinfo/metrics")
        # text_lic = await parser.fetch("/admin/lic")  # если понадобится

        await parse_admin_title(text_title, server, db)
        await parse_admin_pref(text_pref, server, db)
        await parse_sysinfo_metrics(text_metrics, server, db)
        # await parse_admin_lic(text_lic, server, db)  # пока не вызываем
    finally:
        await parser.close()

async def save_admin_links_to_db(db: Session, server_id: int, url: str):
    server = db.query(Server).filter(Server.id == server_id).first()
    if server:
        await parse_server_data(server, db)