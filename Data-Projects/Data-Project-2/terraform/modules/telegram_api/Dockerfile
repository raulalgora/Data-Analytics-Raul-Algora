FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--workers", "2", "--bind=0.0.0.0:8080", "main:app", "--log-level", "debug"]