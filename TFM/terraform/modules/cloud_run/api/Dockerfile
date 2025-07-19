FROM python:3.10-slim

WORKDIR /app

COPY api_server.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080"]