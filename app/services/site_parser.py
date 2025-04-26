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
