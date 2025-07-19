FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and CSV file
COPY . .

# Expose the port that Cloud Run will use
EXPOSE 8080

# Use the PORT environment variable that Cloud Run provides
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080"]