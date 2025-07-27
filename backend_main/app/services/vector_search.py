import vertexai
from vertexai.preview.language_models import TextEmbeddingModel
from google.cloud import aiplatform
from google.cloud.aiplatform import MatchingEngineIndex, MatchingEngineIndexEndpoint
from typing import List, Dict, Any, Optional, Tuple
import logging
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.config import settings
from app.util.logger import get_logger

logger = get_logger(__name__)

class VectorSearchService:
    """Service for vector similarity search using Vertex AI Vector Search"""
    
    def __init__(self):
        # Initialize Vertex AI
        vertexai.init(
            project=settings.GCP_PROJECT_ID,
            location=settings.VERTEX_LOCATION
        )
        
        # Initialize AI Platform
        aiplatform.init(
            project=settings.GCP_PROJECT_ID,
            location=settings.VERTEX_LOCATION
        )
        
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.index_id = settings.VERTEX_INDEX_ID
        self.endpoint_id = settings.VERTEX_ENDPOINT_ID
    
    async def search_similar_vectors(
        self,
        query_embedding: List[float],
        num_neighbors: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using Vertex AI Vector Search
        """
        try:
            logger.info(f"Searching for {num_neighbors} similar vectors")
            
            # Get the deployed index endpoint
            endpoint = MatchingEngineIndexEndpoint(self.endpoint_id)
            
            # Prepare the query
            query = {
                "queries": [{
                    "embedding": query_embedding,
                    "neighbor_count": num_neighbors
                }]
            }
            
            # Add filters if provided
            if filter_metadata:
                query["queries"][0]["filters"] = self._build_filters(filter_metadata)
            
            # Execute search
            loop = asyncio.get_event_loop()
            
            def _sync_search():
                response = endpoint.find_neighbors(query)
                return response
            
            search_response = await loop.run_in_executor(self.executor, _sync_search)
            
            # Process results
            results = []
            if search_response and hasattr(search_response, 'nearest_neighbors'):
                for neighbor in search_response.nearest_neighbors[0]:
                    result = {
                        'id': neighbor.id,
                        'distance': neighbor.distance,
                        'metadata': neighbor.restricts if hasattr(neighbor, 'restricts') else {}
                    }
                    results.append(result)
            
            logger.info(f"Found {len(results)} similar vectors")
            return results
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            raise
    
    def _build_filters(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build filter conditions for vector search
        """
        filters = {}
        
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                filters[key] = value
            elif isinstance(value, list):
                filters[key] = {"in": value}
            elif isinstance(value, dict):
                filters[key] = value
        
        return filters
    
    async def batch_search(
        self,
        query_embeddings: List[List[float]],
        num_neighbors: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Perform batch vector search for multiple queries
        """
        try:
            logger.info(f"Performing batch search for {len(query_embeddings)} queries")
            
            # Get the deployed index endpoint
            endpoint = MatchingEngineIndexEndpoint(self.endpoint_id)
            
            # Prepare batch query
            queries = []
            for embedding in query_embeddings:
                query_item = {
                    "embedding": embedding,
                    "neighbor_count": num_neighbors
                }
                
                if filter_metadata:
                    query_item["filters"] = self._build_filters(filter_metadata)
                
                queries.append(query_item)
            
            query = {"queries": queries}
            
            # Execute batch search
            loop = asyncio.get_event_loop()
            
            def _sync_batch_search():
                response = endpoint.find_neighbors(query)
                return response
            
            search_response = await loop.run_in_executor(self.executor, _sync_batch_search)
            
            # Process batch results
            batch_results = []
            if search_response and hasattr(search_response, 'nearest_neighbors'):
                for query_neighbors in search_response.nearest_neighbors:
                    query_results = []
                    for neighbor in query_neighbors:
                        result = {
                            'id': neighbor.id,
                            'distance': neighbor.distance,
                            'metadata': neighbor.restricts if hasattr(neighbor, 'restricts') else {}
                        }
                        query_results.append(result)
                    batch_results.append(query_results)
            
            logger.info(f"Batch search completed with {len(batch_results)} query results")
            return batch_results
            
        except Exception as e:
            logger.error(f"Batch vector search error: {e}")
            raise
    
    async def search_by_text(
        self,
        query_text: str,
        num_neighbors: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        embedding_service=None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors by converting text to embedding first
        """
        try:
            if not embedding_service:
                from app.services.embedding import EmbeddingService
                embedding_service = EmbeddingService()
            
            # Create embedding for query text
            query_embedding = await embedding_service.embed_query(query_text)
            
            if not query_embedding:
                logger.error("Failed to create embedding for query text")
                return []
            
            # Perform vector search
            results = await self.search_similar_vectors(
                query_embedding,
                num_neighbors,
                filter_metadata
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Text-based vector search error: {e}")
            raise
    
    async def get_vector_by_id(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific vector by its ID
        """
        try:
            # Get the index
            index = MatchingEngineIndex(self.index_id)
            
            # This would require the index to support direct lookup
            # Implementation depends on the specific Vertex AI Vector Search setup
            logger.warning("Direct vector lookup by ID not implemented - requires index configuration")
            return None
            
        except Exception as e:
            logger.error(f"Vector lookup error: {e}")
            return None
    
    async def update_vector_metadata(
        self,
        vector_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update metadata for a specific vector
        Note: This may require re-importing the vector with updated metadata
        """
        try:
            logger.info(f"Updating metadata for vector {vector_id}")
            
            # This would typically require re-importing the vector with updated metadata
            # Implementation depends on the specific Vertex AI Vector Search setup
            logger.warning("Vector metadata update not implemented - requires re-import")
            return False
            
        except Exception as e:
            logger.error(f"Vector metadata update error: {e}")
            return False
    
    async def delete_vector(self, vector_id: str) -> bool:
        """
        Delete a vector from the index
        Note: This may require rebuilding the index or using specific deletion APIs
        """
        try:
            logger.info(f"Deleting vector {vector_id}")
            
            # This would typically require index rebuilding or specific deletion APIs
            # Implementation depends on the specific Vertex AI Vector Search setup
            logger.warning("Vector deletion not implemented - requires index rebuilding")
            return False
            
        except Exception as e:
            logger.error(f"Vector deletion error: {e}")
            return False
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector index
        """
        try:
            # Get the index
            index = MatchingEngineIndex(self.index_id)
            
            # Get index information
            index_info = {
                'index_id': self.index_id,
                'endpoint_id': self.endpoint_id,
                'location': settings.VERTEX_LOCATION,
                'project_id': settings.GCP_PROJECT_ID
            }
            
            # Try to get additional stats if available
            try:
                if hasattr(index, 'description'):
                    index_info['description'] = index.description
                if hasattr(index, 'metadata'):
                    index_info['metadata'] = index.metadata
            except Exception:
                pass
            
            return index_info
            
        except Exception as e:
            logger.error(f"Index stats retrieval error: {e}")
            return {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)