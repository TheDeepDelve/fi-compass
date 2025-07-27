import vertexai
from vertexai.language_models import TextEmbeddingModel
from typing import List, Dict, Any, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import PyPDF2
import io

from app.config import settings
from app.util.logger import get_logger

logger = get_logger(__name__)

class EmbeddingService:
    """Service for creating text embeddings using Vertex AI"""
    
    def __init__(self):
        # Initialize Vertex AI
        vertexai.init(
            project=settings.GCP_PROJECT_ID,
            location=settings.VERTEX_LOCATION
        )
        
        # Initialize embedding model
        self.model = TextEmbeddingModel.from_pretrained(settings.EMBEDDING_MODEL)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def create_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:
        """
        Create embeddings for a list of texts
        """
        try:
            if not texts:
                return []
            
            logger.info(f"Creating embeddings for {len(texts)} texts")
            
            # Process in batches to avoid API limits
            all_embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = await self._create_batch_embeddings(batch)
                all_embeddings.extend(batch_embeddings)
            
            logger.info(f"Successfully created {len(all_embeddings)} embeddings")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Embedding creation error: {e}")
            raise
    
    async def _create_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a batch of texts"""
        loop = asyncio.get_event_loop()
        
        def _sync_embed():
            embeddings = self.model.get_embeddings(texts)
            return [embedding.values for embedding in embeddings]
        
        return await loop.run_in_executor(self.executor, _sync_embed)
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 512,
        overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks for embedding
        """
        if not text or len(text.strip()) == 0:
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_text.strip()) > 0:
                chunks.append({
                    'content': chunk_text,
                    'chunk_id': i // (chunk_size - overlap),
                    'word_count': len(chunk_words),
                    'char_count': len(chunk_text)
                })
            
            # Break if we've reached the end
            if i + chunk_size >= len(words):
                break
        
        return chunks
    
    async def process_document(
        self,
        content: bytes,
        filename: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a document and create embeddings for its chunks
        """
        try:
            logger.info(f"Processing document: {filename}")
            
            # Extract text based on content type
            if content_type == 'application/pdf':
                text = await self._extract_pdf_text(content)
            elif content_type.startswith('text/'):
                text = content.decode('utf-8')
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            if not text or len(text.strip()) == 0:
                raise ValueError("No text content found in document")
            
            # Create chunks
            chunks = self.chunk_text(text)
            
            if not chunks:
                raise ValueError("No valid chunks created from document")
            
            # Create embeddings for chunks
            chunk_texts = [chunk['content'] for chunk in chunks]
            embeddings = await self.create_embeddings(chunk_texts)
            
            # Combine chunks with embeddings
            processed_chunks = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_data = {
                    'id': self._generate_chunk_id(filename, i),
                    'content': chunk['content'],
                    'embedding': embedding,
                    'metadata': {
                        'filename': filename,
                        'content_type': content_type,
                        'chunk_index': i,
                        'word_count': chunk['word_count'],
                        'char_count': chunk['char_count'],
                        **(metadata or {})
                    }
                }
                processed_chunks.append(chunk_data)
            
            logger.info(f"Successfully processed document {filename} into {len(processed_chunks)} chunks")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Document processing error ({filename}): {e}")
            raise
    
    async def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
            
            return '\n'.join(text_parts)
            
        except Exception as e:
            logger.error(f"PDF text extraction error: {e}")
            raise ValueError("Failed to extract text from PDF")
    
    def _generate_chunk_id(self, filename: str, chunk_index: int) -> str:
        """Generate unique ID for a chunk"""
        content = f"{filename}_{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Create embedding for a single query text
        """
        try:
            embeddings = await self.create_embeddings([query])
            return embeddings[0] if embeddings else []
            
        except Exception as e:
            logger.error(f"Query embedding error: {e}")
            raise
    
    async def process_financial_data(
        self,
        financial_data: Dict[str, Any],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Process financial data and create searchable embeddings
        """
        try:
            logger.info(f"Processing financial data for user: {user_id}")
            
            # Convert financial data to text chunks
            text_chunks = self._financial_data_to_text(financial_data)
            
            if not text_chunks:
                return []
            
            # Create embeddings
            texts = [chunk['content'] for chunk in text_chunks]
            embeddings = await self.create_embeddings(texts)
            
            # Combine with metadata
            processed_chunks = []
            for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
                chunk_data = {
                    'id': self._generate_chunk_id(f"financial_data_{user_id}", i),
                    'content': chunk['content'],
                    'embedding': embedding,
                    'metadata': {
                        'user_id': user_id,
                        'data_type': 'financial_data',
                        'category': chunk.get('category', 'general'),
                        'timestamp': chunk.get('timestamp'),
                        **chunk.get('metadata', {})
                    }
                }
                processed_chunks.append(chunk_data)
            
            logger.info(f"Processed financial data into {len(processed_chunks)} searchable chunks")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Financial data processing error: {e}")
            raise
    
    def _financial_data_to_text(self, financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert financial data to text chunks for embedding"""
        chunks = []
        
        # Net worth summary
        if 'net_worth' in financial_data:
            net_worth = financial_data['net_worth']
            text = f"Net worth summary: Total assets ₹{net_worth.get('assets', 0)}, Total liabilities ₹{net_worth.get('liabilities', 0)}, Net worth ₹{net_worth.get('total', 0)}"
            chunks.append({
                'content': text,
                'category': 'net_worth',
                'metadata': {'data_source': 'net_worth_summary'}
            })
        
        # Transactions
        if 'transactions' in financial_data:
            for txn in financial_data['transactions'][:50]:  # Limit to recent 50
                text = f"Transaction: {txn.get('description', '')} Amount: ₹{txn.get('amount', 0)} Category: {txn.get('category', 'Unknown')} Date: {txn.get('date', '')}"
                chunks.append({
                    'content': text,
                    'category': 'transaction',
                    'timestamp': txn.get('date'),
                    'metadata': {'transaction_id': txn.get('id')}
                })
        
        # Investment portfolio
        if 'investments' in financial_data:
            for investment in financial_data['investments']:
                text = f"Investment: {investment.get('name', '')} Type: {investment.get('type', '')} Value: ₹{investment.get('current_value', 0)} Returns: {investment.get('returns', 0)}%"
                chunks.append({
                    'content': text,
                    'category': 'investment',
                    'metadata': {'investment_type': investment.get('type')}
                })
        
        return chunks