"""FastAPI routes for OpenDiscourse API v1."""

from fastapi import APIRouter, HTTPException

api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "OpenDiscourse API is running"}


@api_router.get("/info")
async def get_info():
    """Get API information."""
    return {
        "name": "OpenDiscourse API",
        "version": "0.1.0",
        "description": "API for analyzing political discourse"
    }


@api_router.get("/documents")
async def list_documents():
    """List all documents."""
    # Placeholder implementation
    return {"documents": [], "total": 0}


@api_router.get("/documents/{doc_id}")
async def get_document(doc_id: int):
    """Get a specific document."""
    # Placeholder implementation
    if doc_id <= 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc_id,
        "title": f"Document {doc_id}",
        "content": "Sample content",
        "created_at": "2025-01-01T00:00:00Z"
    }
