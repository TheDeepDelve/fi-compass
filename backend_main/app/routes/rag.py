from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json

from app.services.embedding import EmbeddingService
from app.services.vector_search import VectorSearchService
from app.util.logger import get_logger
from google.cloud import firestore, storage

logger = get_logger(__name__)
router = APIRouter()
db = firestore.Client()

class DocumentUploadResponse(BaseModel):
    success: bool
    document_id: str
    chunks_created: int
    message: str

class DocumentInfo(BaseModel):
    id: str
    filename: str
    content_type: str
    upload_date: str
    chunk_count: int
    metadata: Dict[str, Any]

class SearchRequest(BaseModel):
    query: str
    num_results: int = 5
    filter_by: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_results: int

@router.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: str = Form("{}"),
    current_user: dict = Depends(lambda: {})
):
    """
    Upload and process a document for RAG
    """
    try:
        user_phone = current_user.get("phoneNumber")
        if not user_phone:
            raise HTTPException(status_code=401, detail="User information not found")
        
        # Validate file type
        allowed_types = ['application/pdf', 'text/plain', 'text/markdown']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Parse metadata
        try:
            doc_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            doc_metadata = {}
        
        # Add user context to metadata
        doc_metadata.update({
            'uploaded_by': user_phone,
            'upload_date': datetime.utcnow().isoformat(),
            'file_size': file.size
        })
        
        logger.info(f"Processing document upload: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Process document with embedding service
        embedding_service = EmbeddingService()
        processed_chunks = await embedding_service.process_document(
            content=content,
            filename=file.filename,
            content_type=file.content_type,
            metadata=doc_metadata
        )
        
        if not processed_chunks:
            raise HTTPException(status_code=400, detail="No content could be extracted from document")
        
        # Store embeddings
        vector_search = VectorSearchService()
        storage_result = await vector_search.store_embeddings(processed_chunks)
        
        if not storage_result.get("success"):
            raise HTTPException(status_code=500, detail="Failed to store document embeddings")
        
        # Generate document ID
        document_id = f"doc_{user_phone}_{int(datetime.utcnow().timestamp())}"
        
        # Store document metadata in Firestore
        doc_ref = db.collection('documents').document(document_id)
        doc_ref.set({
            'filename': file.filename,
            'content_type': file.content_type,
            'uploaded_by': user_phone,
            'upload_date': firestore.SERVER_TIMESTAMP,
            'chunk_count': len(processed_chunks),
            'metadata': doc_metadata,
            'storage_method': storage_result.get('storage_method', 'unknown'),
            'chunk_ids': [chunk['id'] for chunk in processed_chunks]
        })
        
        logger.info(f"Document processed successfully: {file.filename}, {len(processed_chunks)} chunks")
        
        return DocumentUploadResponse(
            success=True,
            document_id=document_id,
            chunks_created=len(processed_chunks),
            message=f"Document '{file.filename}' uploaded and processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process document")

@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents(
    limit: int = 20,
    current_user: dict = Depends(lambda: {})
):
    """
    List user's uploaded documents
    """
    try:
        user_phone = current_user.get("phoneNumber")
        if not user_phone:
            raise HTTPException(status_code=401, detail="User information not found")
        
        docs_ref = db.collection('documents')
        query = docs_ref.where('uploaded_by', '==', user_phone)\
                       .order_by('upload_date', direction='DESCENDING')\
                       .limit(limit)
        
        documents = []
        for doc in query.stream():
            doc_data = doc.to_dict()
            documents.append(DocumentInfo(
                id=doc.id,
                filename=doc_data.get('filename', ''),
                content_type=doc_data.get('content_type', ''),
                upload_date=doc_data.get('upload_date', '').isoformat() if doc_data.get('upload_date') else '',
                chunk_count=doc_data.get('chunk_count', 0),
                metadata=doc_data.get('metadata', {})
            ))
        
        return documents
        
    except Exception as e:
        logger.error(f"Document listing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(lambda: {})
):
    """
    Delete a document and its embeddings
    """
    try:
        user_phone = current_user.get("phoneNumber")
        if not user_phone:
            raise HTTPException(status_code=401, detail="User information not found")
        
        # Get document info
        doc_ref = db.collection('documents').document(document_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = doc.to_dict()
        
        # Verify ownership
        if doc_data.get('uploaded_by') != user_phone:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete embeddings
        chunk_ids = doc_data.get('chunk_ids', [])
        if chunk_ids:
            vector_search = VectorSearchService()
            await vector_search.delete_embeddings(chunk_ids)
        
        # Delete document metadata
        doc_ref.delete()
        
        logger.info(f"Document deleted: {document_id}")
        
        return {
            "success": True,
            "message": f"Document '{doc_data.get('filename', document_id)}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document deletion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@router.post("/search", response_model=SearchResponse)
async def search_knowledge_base(
    request: SearchRequest,
    current_user: dict = Depends(lambda: {})
):
    """
    Search through the knowledge base
    """
    try:
        user_phone = current_user.get("phoneNumber")
        if not user_phone:
            raise HTTPException(status_code=401, detail="User information not found")
        
        # Add user filter to search
        filter_by = request.filter_by or {}
        filter_by['uploaded_by'] = user_phone
        
        # Perform search
        vector_search = VectorSearchService()
        results = await vector_search.search_documents(
            query_text=request.query,
            num_results=request.num_results,
            filter_by=filter_by
        )
        
        return SearchResponse(
            results=results,
            query=request.query,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Knowledge base search error: {e}")
        raise HTTPException(status_code=500, detail="Failed to search knowledge base")

@router.post("/embed-financial-data")
async def embed_user_financial_data(
    current_user: dict = Depends(lambda: {})
):
    """
    Create embeddings from user's financial data for personalized search
    """
    try:
        user_phone = current_user.get("phoneNumber")
        mcp_session_id = current_user.get("mcpSessionId")
        
        if not user_phone or not mcp_session_id:
            raise HTTPException(status_code=401, detail="User information not found")
        
        # Fetch comprehensive financial data
        from app.services.mcp_client import MCPClient
        
        async with MCPClient() as mcp_client:
            # Get all available financial data
            financial_data = {}
            
            # Net worth
            net_worth_result = await mcp_client.fetch_net_worth(mcp_session_id)
            if net_worth_result.get("success"):
                financial_data["net_worth"] = net_worth_result.get("data")
            
            # Credit report
            credit_result = await mcp_client.fetch_credit_report(mcp_session_id)
            if credit_result.get("success"):
                financial_data["credit_report"] = credit_result.get("data")
            
            # EPF details
            epf_result = await mcp_client.fetch_epf_details(mcp_session_id)
            if epf_result.get("success"):
                financial_data["epf_details"] = epf_result.get("data")
            
            # Recent transactions
            bank_txn_result = await mcp_client.fetch_bank_transactions(mcp_session_id)
            if bank_txn_result.get("success"):
                financial_data["bank_transactions"] = bank_txn_result.get("data", {}).get("transactions", [])
            
            mf_txn_result = await mcp_client.fetch_mf_transactions(mcp_session_id)
            if mf_txn_result.get("success"):
                financial_data["mf_transactions"] = mf_txn_result.get("data", {}).get("transactions", [])
            
            stock_txn_result = await mcp_client.fetch_stock_transactions(mcp_session_id)
            if stock_txn_result.get("success"):
                financial_data["stock_transactions"] = stock_txn_result.get("data", {}).get("transactions", [])
        
        if not financial_data:
            return {
                "success": False,
                "message": "No financial data available to embed"
            }
        
        # Process financial data into embeddings
        embedding_service = EmbeddingService()
        processed_chunks = await embedding_service.process_financial_data(
            financial_data=financial_data,
            user_id=user_phone
        )
        
        if not processed_chunks:
            return {
                "success": False,
                "message": "No embeddings created from financial data"
            }
        
        # Store embeddings
        vector_search = VectorSearchService()
        storage_result = await vector_search.store_embeddings(processed_chunks)
        
        # Update user's financial data embedding status
        users_ref = db.collection('users')
        users_ref.document(user_phone).update({
            'financial_data_embedded': True,
            'last_financial_embed': firestore.SERVER_TIMESTAMP,
            'financial_chunks_count': len(processed_chunks)
        })
        
        logger.info(f"Financial data embedded for user: {user_phone}, {len(processed_chunks)} chunks")
        
        return {
            "success": True,
            "chunks_created": len(processed_chunks),
            "storage_method": storage_result.get("storage_method"),
            "message": "Financial data embedded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Financial data embedding error: {e}")
        raise HTTPException(status_code=500, detail="Failed to embed financial data")

@router.post("/upload-corpus")
async def upload_knowledge_corpus(
    files: List[UploadFile] = File(...),
    corpus_name: str = Form(...),
    description: str = Form(""),
    current_user: dict = Depends(lambda: {})
):
    """
    Upload multiple documents as a knowledge corpus
    """
    try:
        user_phone = current_user.get("phoneNumber")
        if not user_phone:
            raise HTTPException(status_code=401, detail="User information not found")
        
        if len(files) > 20:  # Limit number of files
            raise HTTPException(status_code=400, detail="Maximum 20 files allowed per corpus")
        
        logger.info(f"Processing corpus upload: {corpus_name} with {len(files)} files")
        
        # Process all files
        embedding_service = EmbeddingService()
        vector_search = VectorSearchService()
        
        total_chunks = 0
        processed_files = []
        
        for file in files:
            try:
                # Validate file type
                if file.content_type not in ['application/pdf', 'text/plain', 'text/markdown']:
                    logger.warning(f"Skipping unsupported file type: {file.filename}")
                    continue
                
                # Read and process file
                content = await file.read()
                
                chunks = await embedding_service.process_document(
                    content=content,
                    filename=file.filename,
                    content_type=file.content_type,
                    metadata={
                        'corpus_name': corpus_name,
                        'corpus_description': description,
                        'uploaded_by': user_phone,
                        'upload_date': datetime.utcnow().isoformat()
                    }
                )
                
                if chunks:
                    # Store embeddings
                    storage_result = await vector_search.store_embeddings(chunks)
                    
                    if storage_result.get("success"):
                        total_chunks += len(chunks)
                        processed_files.append({
                            'filename': file.filename,
                            'chunks': len(chunks)
                        })
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}")
                continue
        
        if total_chunks == 0:
            raise HTTPException(status_code=400, detail="No files could be processed successfully")
        
        # Store corpus metadata
        corpus_id = f"corpus_{user_phone}_{int(datetime.utcnow().timestamp())}"
        corpus_ref = db.collection('corpora').document(corpus_id)
        corpus_ref.set({
            'name': corpus_name,
            'description': description,
            'uploaded_by': user_phone,
            'upload_date': firestore.SERVER_TIMESTAMP,
            'total_files': len(processed_files),
            'total_chunks': total_chunks,
            'processed_files': processed_files
        })
        
        logger.info(f"Corpus uploaded successfully: {corpus_name}, {total_chunks} total chunks")
        
        return {
            "success": True,
            "corpus_id": corpus_id,
            "total_files_processed": len(processed_files),
            "total_chunks_created": total_chunks,
            "message": f"Corpus '{corpus_name}' uploaded and processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Corpus upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload corpus")

@router.get("/corpora")
async def list_corpora(
    current_user: dict = Depends(lambda: {})
):
    """
    List user's uploaded knowledge corpora
    """
    try:
        user_phone = current_user.get("phoneNumber")
        if not user_phone:
            raise HTTPException(status_code=401, detail="User information not found")
        
        corpora_ref = db.collection('corpora')
        query = corpora_ref.where('uploaded_by', '==', user_phone)\
                          .order_by('upload_date', direction='DESCENDING')
        
        corpora = []
        for doc in query.stream():
            doc_data = doc.to_dict()
            corpora.append({
                'id': doc.id,
                'name': doc_data.get('name'),
                'description': doc_data.get('description'),
                'upload_date': doc_data.get('upload_date'),
                'total_files': doc_data.get('total_files', 0),
                'total_chunks': doc_data.get('total_chunks', 0)
            })
        
        return corpora
        
    except Exception as e:
        logger.error(f"Corpora listing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list corpora")

@router.get("/embedding-stats")
async def get_embedding_stats(
    current_user: dict = Depends(lambda: {})
):
    """
    Get statistics about user's embeddings
    """
    try:
        user_phone = current_user.get("phoneNumber")
        if not user_phone:
            raise HTTPException(status_code=401, detail="User information not found")
        
        # Count documents
        docs_ref = db.collection('documents')
        docs_query = docs_ref.where('uploaded_by', '==', user_phone)
        docs_count = len(list(docs_query.stream()))
        
        # Count corpora
        corpora_ref = db.collection('corpora')
        corpora_query = corpora_ref.where('uploaded_by', '==', user_phone)
        corpora_count = len(list(corpora_query.stream()))
        
        # Count total embeddings from Firestore
        embeddings_ref = db.collection('embeddings')
        embeddings_query = embeddings_ref.where('metadata.uploaded_by', '==', user_phone)
        embeddings_count = len(list(embeddings_query.stream()))
        
        # Check financial data embedding status
        user_ref = db.collection('users').document(user_phone)
        user_doc = user_ref.get()
        user_data = user_doc.to_dict() if user_doc.exists else {}
        
        return {
            "total_documents": docs_count,
            "total_corpora": corpora_count,
            "total_embeddings": embeddings_count,
            "financial_data_embedded": user_data.get('financial_data_embedded', False),
            "last_financial_embed": user_data.get('last_financial_embed'),
            "financial_chunks_count": user_data.get('financial_chunks_count', 0)
        }
        
    except Exception as e:
        logger.error(f"Embedding stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get embedding statistics")