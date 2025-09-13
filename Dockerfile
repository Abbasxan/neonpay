# Используем официальный Python образ
FROM python:3.11-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y gcc libffi-dev curl && \
    pip install --upgrade pip

# Создаём директории
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Указываем команду запуска по умолчанию (можно изменить в Procfile)
CMD ["python", "main.py"]
