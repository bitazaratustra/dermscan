# Dockerfile optimizado
FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R 1000:1000 /app \
    && chmod -R 755 /app

USER 1000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
