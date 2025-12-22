FROM python:3.11-slim

WORKDIR /app

# Install Rust and system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable \
    && export PATH="$HOME/.cargo/bin:$PATH" \
    && rm -rf /var/lib/apt/lists/*

# Set Rust environment variables
ENV CARGO_HOME=/root/.cargo
ENV RUSTUP_HOME=/root/.rustup
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements and install Python dependencies
COPY requirements-api.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements-api.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the API server (PORT env var provided by Render)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}


