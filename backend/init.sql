-- EpsteinBase Database Schema
-- CREATE EXTENSION IF NOT EXISTS vector; -- Optional: uncomment if using pgvector image

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    efta_id VARCHAR(20),
    title TEXT,
    source VARCHAR(50) NOT NULL,
    type VARCHAR(50), -- 'video', 'audio', 'image', 'email', 'document'
    subtype VARCHAR(100),
    date_original DATE,
    date_released DATE DEFAULT CURRENT_DATE,
    description TEXT,
    context TEXT,
    ocr_text TEXT,
    original_filename VARCHAR(500),
    file_path VARCHAR(1000),
    thumbnail_path VARCHAR(1000),
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    page_number INT,
    source_pdf VARCHAR(500),
    duration VARCHAR(50),
    location VARCHAR(500),
    url VARCHAR(1000),
    downloadable BOOLEAN DEFAULT true,
    redacted BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE people (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    normalized_name VARCHAR(500),
    aliases TEXT[],
    description TEXT
);

CREATE TABLE document_people (
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    person_id INT REFERENCES people(id) ON DELETE CASCADE,
    relationship VARCHAR(50), -- 'pictured', 'mentioned', 'author', 'recipient'
    PRIMARY KEY (document_id, person_id, relationship)
);

-- Full-text search indexes
CREATE INDEX idx_docs_ocr ON documents USING gin(to_tsvector('english', COALESCE(ocr_text, '') || ' ' || COALESCE(description, '') || ' ' || COALESCE(title, '')));
CREATE INDEX idx_docs_type ON documents(type);
CREATE INDEX idx_docs_source ON documents(source);
CREATE INDEX idx_docs_efta ON documents(efta_id);
CREATE INDEX idx_docs_date ON documents(date_released);
CREATE INDEX idx_people_name ON people(normalized_name);

