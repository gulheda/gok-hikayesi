FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend backend

ENV PYTHONUNBUFFERED=1

# $PORT platform tarafından (Railway/Render/Fly) atanır; yoksa 8000 kullanılır.
CMD ["sh", "-c", "uvicorn app.api.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8000}"]
