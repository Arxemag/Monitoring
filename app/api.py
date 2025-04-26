from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db_session_context
from app.models import Server, Service
from app import schemas
from app.scanner import scan_server_ports
from app.parser import save_admin_links_to_db  # добавил сюда парсер!

router = APIRouter(
    prefix="/api",
    tags=["Monitoring API"]
)

@router.get("/servers", response_model=list[schemas.ServerRead])
def get_servers(db: Session = Depends(get_db_session_context)):
    return db.query(Server).all()

@router.get("/servers/{server_id}", response_model=schemas.ServerRead)
def get_server(server_id: int, db: Session = Depends(get_db_session_context)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@router.post("/servers", response_model=schemas.ServerRead)
async def create_server(server: schemas.ServerCreate, db: Session = Depends(get_db_session_context)):
    db_server = Server(**server.dict())
    db.add(db_server)
    db.commit()
    db.refresh(db_server)

    # После успешного добавления сервера - автопарсинг!
    try:
        await save_admin_links_to_db(db, db_server.id, db_server.url)
    except Exception as e:
        # Можно залогировать ошибку, чтобы не падал API
        print(f"[ERROR] Failed to parse admin links for server {db_server.name}: {str(e)}")

    return db_server

@router.patch("/servers/{server_id}", response_model=schemas.ServerRead)
def update_server(server_id: int, server_update: schemas.ServerUpdate, db: Session = Depends(get_db_session_context)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    update_data = server_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(server, key, value)

    db.commit()
    db.refresh(server)
    return server

@router.delete("/servers/{server_id}")
def delete_server(server_id: int, db: Session = Depends(get_db_session_context)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    db.delete(server)
    db.commit()
    return {"message": "Server deleted successfully"}

@router.get("/services", response_model=list[schemas.ServiceRead])
def get_services(db: Session = Depends(get_db_session_context)):
    return db.query(Service).all()

@router.post("/scan/{server_id}")
async def scan_server(server_id: int, db: Session = Depends(get_db_session_context)):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    await scan_server_ports(db, server)
    return {"message": f"Ports scanned for server {server.name}", "ports": server.ports}
