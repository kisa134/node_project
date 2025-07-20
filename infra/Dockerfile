FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock* ./

# Установка Poetry
RUN pip install poetry

# Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Копирование кода приложения
COPY . .

# Создание необходимых директорий
RUN mkdir -p /app/data /app/torrents /app/logs

# Порт по умолчанию
EXPOSE 8888

# Запуск приложения
CMD ["python", "-m", "torrentnode.node"] 