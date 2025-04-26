import sys
from app.database import init_db, get_db_session, seed_servers

def main():
    if len(sys.argv) < 2:
        print("Укажите команду: init / seed")
        return

    command = sys.argv[1]

    if command == "init":
        print("Инициализация базы данных...")
        init_db()
        print("База данных создана.")

    elif command == "seed":
        print("Заполнение базы начальными данными...")
        with get_db_session() as db:
            seed_servers(db)
        print("База данных заполнена начальными данными.")

    else:
        print(f"Неизвестная команда: {command}")

if __name__ == "__main__":
    main()
