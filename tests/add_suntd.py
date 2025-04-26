from app.database import get_db_session
from app.models import Server
from datetime import datetime

def main():
    with get_db_session() as db:
        new_server = Server(
            name="SUNTD",
            ip_or_domain="suntd.kodeks.expert",
            ports=None,  # пока нет информации о портах
            is_active=True,
            created_at=datetime.utcnow(),
            meta_info=None
        )
        db.add(new_server)
        db.commit()
        print("Сервер SUNTD успешно добавлен!")

if __name__ == "__main__":
    main()
