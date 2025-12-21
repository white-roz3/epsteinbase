FROM python:3.11-slim

WORKDIR /app

# Install system deps for PyMuPDF and Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libmupdf-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the API server (PORT env var provided by Railway)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}


