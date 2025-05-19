FROM python:3.10-slim

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "sleep 15 && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]