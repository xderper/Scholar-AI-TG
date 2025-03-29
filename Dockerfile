# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код проекта в контейнер
COPY . .

# Создаем директорию для логов
RUN mkdir -p logs

# Устанавливаем переменную окружения для Python, чтобы не создавать .pyc файлы
ENV PYTHONDONTWRITEBYTECODE=1
# Устанавливаем переменную окружения для Python, чтобы не буферизировать stdout и stderr
ENV PYTHONUNBUFFERED=1

# Запускаем бота при старте контейнера
CMD ["python", "run.py"]