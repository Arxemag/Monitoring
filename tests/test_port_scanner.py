import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.models import Server
from app.services import port_scanner

@pytest.mark.asyncio
async def test_scan_server_ports_success():
    server = Server(id=1, name="TEST_SERVER", ip_or_domain="localhost")

    # Патчим aiohttp.ClientSession.get чтобы не делать реальные запросы
    with patch("app.services.port_scanner.aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response

        open_ports = await port_scanner.scan_server(server)

        assert isinstance(open_ports, list)
        assert len(open_ports) > 0
        print(f"[OK] Найдены открытые порты: {open_ports}")

@pytest.mark.asyncio
async def test_scan_server_no_open_ports():
    server = Server(id=1, name="NO_PORTS_SERVER", ip_or_domain="localhost")

    # Патчим чтобы возвращать 500 ошибки
    with patch("app.services.port_scanner.aiohttp.ClientSession.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_get.return_value.__aenter__.return_value = mock_response

        open_ports = await port_scanner.scan_server(server)

        assert open_ports == []
        print("[OK] Нет открытых портов, как ожидалось.")

@pytest.mark.asyncio
async def test_scan_server_connection_errors():
    server = Server(id=1, name="CONNECTION_ERROR_SERVER", ip_or_domain="localhost")

    # Патчим чтобы выбрасывать ошибку соединения
    with patch("app.services.port_scanner.aiohttp.ClientSession.get", side_effect=Exception("Connection failed")):
        open_ports = await port_scanner.scan_server(server)

        assert open_ports == []
        print("[OK] Ошибки соединения обработаны корректно.")

def test_save_ports_to_server_success():
    server = Server(id=1, name="TEST_SERVER", ip_or_domain="localhost")
    server.ports = ""

    mock_db = MagicMock()

    ports = [80, 443, 8080]
    port_scanner.save_ports_to_server(server, ports, mock_db)

    assert server.ports == "80,443,8080"
    print(f"[OK] Порты сохранены корректно: {server.ports}")

def test_main_server_not_found():
    with patch("app.services.port_scanner.get_db_session") as mock_get_db_session:
        mock_db = MagicMock()
        mock_db.query().filter_by().first.return_value = None
        mock_get_db_session.return_value.__enter__.return_value = mock_db

        port_scanner.main()

        from unittest.mock import call

        mock_db.query.assert_has_calls([
            call(Server),
            call().filter_by(name='SUNTD')
        ])
        print("[OK] Отработана ситуация отсутствия сервера.")
