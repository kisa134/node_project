# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
# Мы используем --no-cache-dir, чтобы не хранить лишний кэш в слое образа
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта в контейнер
COPY . .

# Эта команда будет выполняться по умолчанию, если не указана другая в docker-compose.yml
CMD ["python", "scripts/run_neuron.py"] 