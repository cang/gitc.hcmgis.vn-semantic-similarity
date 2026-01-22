FROM python:3.11-slim

WORKDIR /app

COPY shared /app/shared
COPY services/embedding /app/services/embedding

RUN pip install --no-cache-dir -r services/embedding/requirements.txt

ENV PYTHONPATH=/app

## HTTP
CMD ["uvicorn", "services.embedding.main:app", "--host", "0.0.0.0", "--port", "8001"]