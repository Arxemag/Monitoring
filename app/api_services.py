from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.models import Service
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.utils import make_response

router = APIRouter()

# --- CRUD для служб ---

@router.post("/services/")
async def create_service(service: ServiceCreate, db: Session = Depends(get_db_session)):
    new_service = Service(
        server_id=service.server_id,
        port=service.port,
        status=service.status
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return make_response(True, "Служба создана", {
        "id": new_service.id,
        "server_id": new_service.server_id,
        "port": new_service.port,
        "status": new_service.status
    })

@router.get("/services/")
async def list_services(db: Session = Depends(get_db_session)):
    services = db.query(Service).all()
    services_list = [
        {
            "id": s.id,
            "server_id": s.server_id,
            "port": s.port,
            "status": s.status
        } for s in services
    ]
    return make_response(True, "Список служб", services_list)

@router.get("/services/{service_id}")
async def get_service(service_id: int, db: Session = Depends(get_db_session)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        return make_response(False, "Служба не найдена", None)

    return make_response(True, "Информация о службе", {
        "id": service.id,
        "server_id": service.server_id,
        "port": service.port,
        "status": service.status
    })

@router.put("/services/{service_id}")
async def update_service(service_id: int, updated_service: ServiceUpdate, db: Session = Depends(get_db_session)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        return make_response(False, "Служба не найдена", None)

    service.server_id = updated_service.server_id
    service.port = updated_service.port
    service.status = updated_service.status

    db.commit()
    db.refresh(service)

    return make_response(True, "Служба обновлена", {
        "id": service.id,
        "server_id": service.server_id,
        "port": service.port,
        "status": service.status
    })

@router.delete("/services/{service_id}")
async def delete_service(service_id: int, db: Session = Depends(get_db_session)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        return make_response(False, "Служба не найдена", None)

    db.delete(service)
    db.commit()

    return make_response(True, "Служба удалена", None)
