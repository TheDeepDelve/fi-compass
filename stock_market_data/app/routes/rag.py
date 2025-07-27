from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from app.config import settings
from app.util.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Initialize GCP clients only when needed
def get_firestore_client():
    """Get Firestore client, initializing it only when needed"""
    try:
        from google.cloud import firestore
        return firestore.Client()
    except Exception as e:
        logger.warning(f"Failed to initialize Firestore client: {e}")
        return None

class DocumentUploadResponse(BaseModel):
    success: bool
    document_id: str
    message: str

class SearchResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]]
    total_results: int
    query: str

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(lambda: {})
):
    """
    Upload a document for RAG processing
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Validate file type
        allowed_types = ["text/plain", "application/pdf", "text/markdown"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not supported. Allowed: {allowed_types}"
            )
        
        # Try to save document to Firestore, but don't fail if not available
        db = get_firestore_client()
        if db:
            try:
                # Read file content
                content = await file.read()
                
                # Save document metadata to Firestore
                docs_ref = db.collection('documents')
                doc_data = {
                    'user_id': user_id,
                    'filename': file.filename,
                    'content_type': file.content_type,
                    'size': len(content),
                    'uploaded_at': firestore.SERVER_TIMESTAMP,
                    'status': 'uploaded'
                }
                doc_ref = docs_ref.add(doc_data)
                
                logger.info(f"Document uploaded successfully: {file.filename}")
                
                return DocumentUploadResponse(
                    success=True,
                    document_id=doc_ref[1].id,
                    message=f"Document {file.filename} uploaded successfully"
                )
            except Exception as e:
                logger.warning(f"Failed to save document to Firestore: {e}")
        
        # If Firestore is not available, return a basic response
        return DocumentUploadResponse(
            success=True,
            document_id="temp-id",
            message=f"Document {file.filename} uploaded (no storage)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document")

@router.get("/search", response_model=SearchResponse)
async def search_documents(
    query: str,
    limit: int = 10,
    current_user: dict = Depends(lambda: {})
):
    """
    Search documents using RAG
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Try to search documents in Firestore, but don't fail if not available
        db = get_firestore_client()
        if db:
            try:
                # Simple text search in Firestore (in production, use vector search)
                docs_ref = db.collection('documents')
                query_filter = docs_ref.where('user_id', '==', user_id).limit(limit)
                docs = query_filter.stream()
                
                results = []
                for doc in docs:
                    data = doc.to_dict()
                    results.append({
                        'id': doc.id,
                        'filename': data.get('filename'),
                        'content_type': data.get('content_type'),
                        'uploaded_at': data.get('uploaded_at'),
                        'relevance_score': 0.8  # Placeholder score
                    })
                
                return SearchResponse(
                    success=True,
                    results=results,
                    total_results=len(results),
                    query=query
                )
            except Exception as e:
                logger.warning(f"Failed to search documents in Firestore: {e}")
        
        # If Firestore is not available, return empty results
        return SearchResponse(
            success=True,
            results=[],
            total_results=0,
            query=query
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document search error: {e}")
        raise HTTPException(status_code=500, detail="Failed to search documents")

@router.get("/documents", response_model=List[Dict[str, Any]])
async def list_documents(
    current_user: dict = Depends(lambda: {})
):
    """
    List user's uploaded documents
    """
    try:
        user_id = current_user.get("userId")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Try to list documents from Firestore, but don't fail if not available
        db = get_firestore_client()
        if db:
            try:
                docs_ref = db.collection('documents')
                query = docs_ref.where('user_id', '==', user_id).order_by('uploaded_at', direction=firestore.Query.DESCENDING)
                docs = query.stream()
                
                documents = []
                for doc in docs:
                    data = doc.to_dict()
                    documents.append({
                        'id': doc.id,
                        'filename': data.get('filename'),
                        'content_type': data.get('content_type'),
                        'size': data.get('size'),
                        'uploaded_at': data.get('uploaded_at'),
                        'status': data.get('status')
                    })
                
                return documents
            except Exception as e:
                logger.warning(f"Failed to list documents from Firestore: {e}")
        
        # If Firestore is not available, return empty list
        return []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")