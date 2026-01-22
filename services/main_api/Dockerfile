FROM python:3.11-slim

WORKDIR /app

COPY shared /app/shared
COPY services/main_api /app/services/main_api

RUN pip install --no-cache-dir -r services/main_api/requirements.txt

ENV PYTHONPATH=/app
#ENV DB_HOST=localhost DB_PORT=5432

CMD ["uvicorn", "services.main_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

