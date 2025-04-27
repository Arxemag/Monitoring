import aiohttp

async def find_admin_panels(base_url: str) -> list[str]:
    found_panels = []

    url = base_url.rstrip("/") + "/admin"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    found_panels.append(url)
    except Exception:
        pass  # Игнорируем ошибки

    return found_panels

class SiteParser:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session: aiohttp.ClientSession | None = None
        self.logged_in = False

    async def login(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

        login_url = f"{self.base_url}/admin"

        possible_passwords = ["skedoks", "kodeks", "skedok"]

        for password in possible_passwords:
            try:
                async with self.session.post(
                    login_url,
                    data={"username": "kodeks", "password": password},
                    timeout=5
                ) as response:
                    print(f"[DEBUG] Пробуем логин kodeks:{password}")
                    if response.status in (200, 302):
                        print(f"[DEBUG] Логин успешен с паролем: {password}")
                        self.logged_in = True
                        return
            except Exception as e:
                print(f"[DEBUG] Ошибка логина: {e}")
                continue

        raise Exception("Login failed for all password variants")

    async def fetch(self, path: str) -> str:
        if not self.logged_in:
            await self.login()

        if self.session is None:
            raise Exception("Session not initialized")

        url = f"{self.base_url}{path}"
        async with self.session.get(url, timeout=10) as response:
            response.raise_for_status()
            return await response.text()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None
