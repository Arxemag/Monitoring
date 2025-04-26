# Базовый образ с Python 3.11
FROM python:3.11-slim

# Обновляем пакеты и ставим библиотеки для Playwright
RUN apt-get update && apt-get install -y \
    wget gnupg2 fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 \
    libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 xdg-utils libu2f-udev libvulkan1 libxss1 && \
    apt-get clean

# Установим Playwright + браузеры
RUN pip install playwright && playwright install chromium

# Копируем проект в контейнер
WORKDIR /app
COPY . .

# Установим Python-зависимости
RUN pip install -r requirements.txt

# Откроем порт 8000 для FastAPI
EXPOSE 8000

# Стартуем приложение через Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
