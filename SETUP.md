# EpsteinBase Setup Guide

Complete guide to setting up the EpsteinBase full-stack application.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 16+ (or use Docker)
- Docker & Docker Compose (optional, recommended)

## Quick Start (Docker)

```bash
# 1. Start database and API
docker-compose up -d db

# Wait for database to be ready, then:
docker-compose up api

# 2. Initialize database schema
psql -h localhost -U postgres -d epsteinbase -f backend/init.sql

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Download and process data
cd scripts
python download_data.py
python extract_images.py

# 5. Ingest data into database
python ingest_extracted.py
python ingest_huggingface.py

# 6. Start frontend (in new terminal)
cd ../..
npm install
npm run dev
```

## Manual Setup

### 1. Database Setup

```bash
# Create database
createdb epsteinbase

# Run schema
psql -d epsteinbase -f backend/init.sql
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL="postgresql://postgres:postgres@localhost/epsteinbase"

# Download data
cd scripts
python download_data.py

# Extract images from PDFs (this may take a while)
python extract_images.py

# Ingest data
python ingest_extracted.py
python ingest_huggingface.py

# Start API server
cd ..
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
# Install dependencies
npm install

# Create .env file (if not exists)
echo "VITE_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

## Data Sources

The application ingests data from:

1. **Internet Archive**: Combined PDF files (~33,000 pages)
2. **DOJ**: Direct video and audio files
3. **HuggingFace**: Pre-processed EPSTEIN_FILES_20K dataset (~20,000 documents)

## API Endpoints

- `GET /api/stats` - Get database statistics
- `GET /api/documents` - List documents with filtering
- `GET /api/documents/{id}` - Get single document
- `GET /api/search?q={query}` - Full-text search
- `GET /api/people` - Get people mentioned in documents

## Troubleshooting

### Database Connection Error

Make sure PostgreSQL is running:
```bash
# Check status
pg_isready

# Or with Docker
docker-compose ps db
```

### Images Not Loading

- Check that extraction completed successfully
- Verify files exist in `data/extracted/` and `data/thumbnails/`
- Ensure API is serving files from `/files` endpoint

### Search Not Working

- Verify full-text search indexes were created:
  ```sql
  \d documents
  ```
- Check that documents have `ocr_text` populated

### HuggingFace Dataset Download Fails

The dataset requires the `datasets` library:
```bash
pip install datasets
```

## Production Deployment

1. Build frontend:
   ```bash
   npm run build
   ```

2. Serve with nginx or similar

3. Run API with production server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

4. Use environment variables for configuration:
   ```bash
   export DATABASE_URL="postgresql://..."
   export VITE_API_URL="https://api.yourdomain.com"
   ```



