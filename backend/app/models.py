from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class Document(BaseModel):
    id: Optional[int] = None
    efta_id: Optional[str] = None
    title: Optional[str] = None
    source: str
    type: Optional[str] = None
    subtype: Optional[str] = None
    date_original: Optional[date] = None
    date_released: Optional[date] = None
    description: Optional[str] = None
    context: Optional[str] = None
    ocr_text: Optional[str] = None
    original_filename: Optional[str] = None
    file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    page_number: Optional[int] = None
    source_pdf: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: Optional[datetime] = None

class DocumentResponse(BaseModel):
    id: int
    efta_id: Optional[str]
    title: Optional[str]
    source: str
    type: Optional[str]
    subtype: Optional[str]
    description: Optional[str]
    context: Optional[str]
    file_path: Optional[str]
    thumbnail_path: Optional[str]
    ocr_text: Optional[str]
    metadata: Dict[str, Any]
    date_released: Optional[date]
    people: Optional[List[str]] = None

class SearchResponse(BaseModel):
    results: List[DocumentResponse]
    total: int
    page: int
    per_page: int

class StatsResponse(BaseModel):
    total_documents: int
    by_type: Dict[str, int]
    by_source: Dict[str, int]


