# Dockerfile (minimal)
FROM python:3.11-slim

WORKDIR /app
COPY fibonacci_server.py .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir flask requests


CMD ["python", "fibonacci_server.py"]
