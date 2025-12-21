# EpsteinBase

EpsteinBase - Document Database Platform that aggregates all publicly released Epstein files.

A full-stack web application providing searchable access to over 50,000+ documents, images, videos, and audio files from official government releases.

## Architecture

- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: FastAPI + PostgreSQL + pgvector
- **Data Sources**: DOJ, House Oversight, Internet Archive, HuggingFace
- **Features**: Full-text search, image extraction, OCR, pagination

## Quick Start

See [SETUP.md](./SETUP.md) for detailed installation instructions.

### Docker (Recommended)

```bash
# Start database
docker-compose up -d db

# Initialize schema
psql -h localhost -U postgres -d epsteinbase -f backend/init.sql

# Install backend deps
cd backend && pip install -r requirements.txt

# Download and process data
cd scripts
python download_data.py
python extract_images.py  # May take hours for large PDFs

# Ingest data
python ingest_extracted.py
python ingest_huggingface.py

# Start backend
cd .. && uvicorn app.main:app --reload

# In another terminal, start frontend
cd .. && npm install && npm run dev
```

## Features

- **Full-Text Search**: Search across OCR'd text, descriptions, and titles
- **Category Filtering**: Browse by type (video, audio, photo, document, email)
- **Source Filtering**: Filter by data source (DOJ, House Oversight, etc.)
- **Image Extraction**: Automatic extraction of images from PDFs
- **Thumbnail Generation**: Auto-generated thumbnails for all images
- **Modal View**: Detailed view with full image and OCR text
- **Pagination**: Efficient pagination for large result sets

## API Endpoints

- `GET /api/stats` - Database statistics
- `GET /api/documents` - List documents (supports `type`, `source`, `page`, `per_page`)
- `GET /api/documents/{id}` - Get single document with full details
- `GET /api/search?q={query}` - Full-text search with ranking
- `GET /api/people` - Get people mentioned in documents

## Project Structure

```
epsteinbase/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── database.py      # Database connection
│   │   ├── models.py        # Pydantic models
│   │   └── routers/         # API route handlers
│   ├── scripts/
│   │   ├── download_data.py      # Download from sources
│   │   ├── extract_images.py     # Extract images from PDFs
│   │   ├── ingest_extracted.py   # Ingest extracted images
│   │   └── ingest_huggingface.py # Ingest HuggingFace dataset
│   ├── requirements.txt
│   └── init.sql             # Database schema
├── src/
│   ├── App.jsx              # Main React component
│   ├── main.jsx             # React entry point
│   └── index.css            # Tailwind CSS
├── data/                    # Data files (created during setup)
│   ├── pdfs/
│   ├── images/
│   ├── videos/
│   ├── audio/
│   ├── extracted/
│   └── thumbnails/
└── docker-compose.yml
```

## Tech Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- Lucide React (icons)

### Backend
- FastAPI
- PostgreSQL 16
- asyncpg
- PyMuPDF (PDF processing)
- Pillow (image processing)
- HuggingFace Datasets

## Data Statistics

After full ingestion:
- **33,000+** PDF pages extracted from DOJ releases
- **20,000+** documents from HuggingFace dataset
- **10+** video files from BOP surveillance
- **11+** audio files from Maxwell proffer sessions
- **Full-text search** across all OCR'd content

## Development

### Frontend

```bash
npm install
npm run dev        # Start dev server (http://localhost:5173)
npm run build      # Build for production
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload  # Start API (http://localhost:8000)
```

## Environment Variables

Create a `.env` file in the root:

```bash
VITE_API_URL=http://localhost:8000
```

Backend uses:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost/epsteinbase
```

## License

Public records aggregator. All documents sourced from official government releases.

