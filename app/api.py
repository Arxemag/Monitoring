from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db_session
from app.models import Server, ServerInfo, CatalogStatus
from app.schemas.server import ServerCreate, ServerUpdate
from app.services.port_scanner import scan_server_ports
from app.services.parser import save_admin_links_to_db
from app.utils import make_response

router = APIRouter()

# --- CRUD сервера ---

@router.post("/api/servers/")
async def create_server(server: ServerCreate, db: Session = Depends(get_db_session)):
    new_server = Server(
        name=server.name,
        ip_or_domain=server.ip_or_domain,
        ports=server.ports,
        is_active=server.is_active,
        meta_info=server.meta_info
    )
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    return make_response(True, "Сервер создан", {
        "id": new_server.id,
        "name": new_server.name,
        "ip_or_domain": new_server.ip_or_domain,
        "ports": new_server.ports
    })

@router.get("/api/servers/")
async def list_servers(db: Session = Depends(get_db_session)):
    servers = db.query(Server).all()
    servers_list = [
        {
            "id": s.id,
            "name": s.name,
            "ip_or_domain": s.ip_or_domain,
            "ports": s.ports
        } for s in servers
    ]
    return make_response(True, "Список серверов", servers_list)

@router.get("/api/servers/{server_id}")
async def get_server_details(server_id: int, db: Session = Depends(get_db_session)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        return make_response(False, "Сервер не найден", None)

    ports = [int(port.strip()) for port in server.ports.split(",") if port.strip().isdigit()]
    infos = db.query(ServerInfo).filter(ServerInfo.server_id == server_id).all()
    catalogs = db.query(CatalogStatus).filter(CatalogStatus.server_id == server_id).all()

    infos_list = [
        {
            "port": info.port,
            "registration_number": info.registration_number,
            "expiration_date": str(info.expiration_date) if info.expiration_date else None,
            "license_limit": info.license_limit,
            "sessions_count": info.sessions_count,
            "backup_time": info.backup_time,
            "restart_time": info.restart_time,
        }
        for info in infos
    ]

    catalogs_list = [
        {
            "port": catalog.port,
            "path": catalog.path,
            "main_page_status": catalog.main_page_status,
            "db_status": catalog.db_status,
        }
        for catalog in catalogs
    ]

    return make_response(True, "Информация о сервере", {
        "id": server.id,
        "name": server.name,
        "ip_or_domain": server.ip_or_domain,
        "ports": ports,
        "infos": infos_list,
        "catalogs": catalogs_list,
    })

@router.put("/api/servers/{server_id}")
async def update_server(server_id: int, updated_server: ServerUpdate, db: Session = Depends(get_db_session)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        return make_response(False, "Сервер не найден", None)

    server.name = updated_server.name
    server.ip_or_domain = updated_server.ip_or_domain
    server.ports = updated_server.ports
    server.is_active = updated_server.is_active
    server.meta_info = updated_server.meta_info

    db.commit()
    db.refresh(server)

    return make_response(True, "Сервер обновлён", {
        "id": server.id,
        "name": server.name,
        "ip_or_domain": server.ip_or_domain,
        "ports": server.ports
    })

@router.delete("/api/servers/{server_id}")
async def delete_server(server_id: int, db: Session = Depends(get_db_session)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        return make_response(False, "Сервер не найден", None)

    db.delete(server)
    db.commit()

    return make_response(True, "Сервер удалён", None)

# --- Сканирование портов ---
@router.post("/api/servers/{server_id}/scan_ports")
async def scan_ports(server_id: int, db: Session = Depends(get_db_session)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        return make_response(False, "Сервер не найден", None)

    open_ports = await scan_server_ports(server)
    return make_response(True, "Порты отсканированы", {"ports": open_ports})

# --- Парсинг админки ---
@router.post("/api/servers/{server_id}/parse_admin")
async def parse_admin(server_id: int, db: Session = Depends(get_db_session)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        return make_response(False, "Сервер не найден", None)

    await save_admin_links_to_db(db, server_id)
    return make_response(True, "Парсинг админки завершён", None)
