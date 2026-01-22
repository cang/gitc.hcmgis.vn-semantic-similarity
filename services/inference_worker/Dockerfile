#FROM python:3.11-slim
FROM pytorch/pytorch:latest

WORKDIR /app

COPY shared /app/shared
COPY services/inference_worker /app/services/inference_worker

RUN pip install --no-cache-dir -r services/inference_worker/requirements.txt

ENV PYTHONPATH=/app
#ENV PYTHONUNBUFFERED=1
#python -u inference_worker.py
CMD ["python", "services/inference_worker/worker.py"]
