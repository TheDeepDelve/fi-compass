import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession
from typing import List, Dict, Any, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

from app.config import settings
from app.util.logger import get_logger
from app.services.vector_search import VectorSearchService
from app.services.embedding import EmbeddingService

logger = get_logger(__name__)

class GeminiService:
    """Service for Gemini LLM integration with RAG capabilities"""
    
    def __init__(self):
        # Initialize Vertex AI
        vertexai.init(
            project=settings.GCP_PROJECT_ID,
            location=settings.VERTEX_LOCATION
        )
        
        # Initialize Gemini model
        self.model = GenerativeModel(settings.GEMINI_MODEL_NAME)
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Initialize supporting services
        self.vector_search = VectorSearchService()
        self.embedding_service = EmbeddingService()
        
        # System prompt template
        self.system_prompt = """You are a helpful financial wellness assistant for Fi Money users. You have access to the user's financial data, market information, and financial literacy resources.

Your role is to:
1. Provide personalized financial advice based on the user's data
2. Answer questions about their financial health and investments
3. Explain financial concepts in simple terms
4. Help users understand their spending patterns and investment performance
5. Suggest ways to improve financial wellness

Always be:
- Professional but friendly
- Accurate and data-driven
- Educational and informative
- Privacy-conscious (don't share specific financial details unless the user asks)
- Helpful in guiding users toward better financial decisions

Use the provided context to give relevant and personalized responses."""
    
    async def generate_response(
        self,
        user_message: str,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_context_chunks: int = 5
    ) -> Dict[str, Any]:
        """
        Generate a response using Gemini with RAG context
        """
        try:
            logger.info(f"Generating response for user {user_id}")
            
            # Step 1: Create embedding for user query
            query_embedding = await self.embedding_service.embed_query(user_message)
            
            if not query_embedding:
                logger.error("Failed to create query embedding")
                return {
                    "success": False,
                    "error": "Failed to process query",
                    "response": "I'm sorry, I'm having trouble processing your request right now."
                }
            
            # Step 2: Search for relevant context
            context_chunks = await self._retrieve_relevant_context(
                query_embedding, 
                user_id, 
                max_context_chunks
            )
            
            # Step 3: Build prompt with context
            prompt = await self._build_rag_prompt(
                user_message, 
                context_chunks, 
                conversation_history
            )
            
            # Step 4: Generate response using Gemini
            response = await self._generate_gemini_response(prompt)
            
            # Step 5: Log conversation
            await self._log_conversation(user_id, user_message, response, context_chunks)
            
            return {
                "success": True,
                "response": response,
                "context_used": len(context_chunks),
                "sources": [chunk.get('metadata', {}).get('filename', 'Unknown') for chunk in context_chunks]
            }
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I'm sorry, I encountered an error while processing your request. Please try again."
            }
    
    async def _retrieve_relevant_context(
        self,
        query_embedding: List[float],
        user_id: str,
        max_chunks: int
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context using vector search
        """
        try:
            # Search for relevant vectors
            search_results = await self.vector_search.search_similar_vectors(
                query_embedding,
                num_neighbors=max_chunks,
                filter_metadata={"user_id": user_id}
            )
            
            # Get full context for each result
            context_chunks = []
            for result in search_results:
                # Try to get additional context from Firestore or other sources
                chunk_data = await self._get_chunk_context(result['id'])
                if chunk_data:
                    context_chunks.append(chunk_data)
            
            logger.info(f"Retrieved {len(context_chunks)} context chunks")
            return context_chunks
            
        except Exception as e:
            logger.error(f"Context retrieval error: {e}")
            return []
    
    async def _get_chunk_context(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full context data for a chunk ID
        This would typically fetch from Firestore or another storage system
        """
        try:
            # For now, return a placeholder - in production this would fetch from storage
            return {
                'id': chunk_id,
                'content': f"Context chunk {chunk_id}",
                'metadata': {
                    'filename': 'financial_data',
                    'category': 'general'
                }
            }
        except Exception as e:
            logger.error(f"Chunk context retrieval error: {e}")
            return None
    
    async def _build_rag_prompt(
        self,
        user_message: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Build a RAG prompt with context and conversation history
        """
        try:
            # Build context section
            context_section = ""
            if context_chunks:
                context_section = "Relevant Context:\n"
                for i, chunk in enumerate(context_chunks, 1):
                    context_section += f"{i}. {chunk.get('content', '')}\n"
                context_section += "\n"
            
            # Build conversation history
            history_section = ""
            if conversation_history:
                history_section = "Conversation History:\n"
                for msg in conversation_history[-5:]:  # Last 5 messages
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    history_section += f"{role.capitalize()}: {content}\n"
                history_section += "\n"
            
            # Build final prompt
            prompt = f"""{self.system_prompt}

{history_section}{context_section}User Question: {user_message}

Please provide a helpful and informative response based on the context provided. If the context doesn't contain relevant information, you can provide general financial advice but mention that you don't have specific data about their situation."""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Prompt building error: {e}")
            return f"{self.system_prompt}\n\nUser Question: {user_message}"
    
    async def _generate_gemini_response(self, prompt: str) -> str:
        """
        Generate response using Gemini model
        """
        try:
            loop = asyncio.get_event_loop()
            
            def _sync_generate():
                response = self.model.generate_content(prompt)
                return response.text
            
            response_text = await loop.run_in_executor(self.executor, _sync_generate)
            
            if not response_text:
                return "I'm sorry, I couldn't generate a response. Please try again."
            
            return response_text
            
        except Exception as e:
            logger.error(f"Gemini response generation error: {e}")
            return "I'm sorry, I encountered an error while generating a response. Please try again."
    
    async def _log_conversation(
        self,
        user_id: str,
        user_message: str,
        assistant_response: str,
        context_chunks: List[Dict[str, Any]]
    ):
        """
        Log conversation for analytics and improvement
        """
        try:
            # This would typically save to Firestore or BigQuery
            conversation_log = {
                'user_id': user_id,
                'timestamp': asyncio.get_event_loop().time(),
                'user_message': user_message,
                'assistant_response': assistant_response,
                'context_chunks_used': len(context_chunks),
                'context_sources': [chunk.get('metadata', {}).get('filename', 'Unknown') for chunk in context_chunks]
            }
            
            logger.info(f"Conversation logged for user {user_id}")
            
        except Exception as e:
            logger.error(f"Conversation logging error: {e}")
    
    async def analyze_financial_health(
        self,
        financial_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Analyze user's financial health using Gemini
        """
        try:
            logger.info(f"Analyzing financial health for user {user_id}")
            
            # Convert financial data to text for analysis
            analysis_prompt = self._build_financial_analysis_prompt(financial_data)
            
            # Generate analysis
            analysis_response = await self._generate_gemini_response(analysis_prompt)
            
            return {
                "success": True,
                "analysis": analysis_response,
                "data_points_analyzed": len(financial_data.keys())
            }
            
        except Exception as e:
            logger.error(f"Financial health analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": "Unable to analyze financial health at this time."
            }
    
    def _build_financial_analysis_prompt(self, financial_data: Dict[str, Any]) -> str:
        """
        Build prompt for financial health analysis
        """
        # Convert financial data to structured text
        data_summary = "Financial Data Summary:\n"
        
        if 'net_worth' in financial_data:
            net_worth = financial_data['net_worth']
            data_summary += f"Net Worth: ₹{net_worth.get('total', 0)}\n"
            data_summary += f"Assets: ₹{net_worth.get('assets', 0)}\n"
            data_summary += f"Liabilities: ₹{net_worth.get('liabilities', 0)}\n"
        
        if 'transactions' in financial_data:
            transactions = financial_data['transactions']
            data_summary += f"Recent Transactions: {len(transactions)} transactions\n"
            
            # Analyze spending patterns
            total_spending = sum(t.get('amount', 0) for t in transactions if t.get('amount', 0) < 0)
            total_income = sum(t.get('amount', 0) for t in transactions if t.get('amount', 0) > 0)
            
            data_summary += f"Total Spending: ₹{abs(total_spending)}\n"
            data_summary += f"Total Income: ₹{total_income}\n"
        
        if 'investments' in financial_data:
            investments = financial_data['investments']
            data_summary += f"Investment Portfolio: {len(investments)} investments\n"
            
            total_investment_value = sum(inv.get('current_value', 0) for inv in investments)
            data_summary += f"Total Investment Value: ₹{total_investment_value}\n"
        
        prompt = f"""{self.system_prompt}

Please analyze the following financial data and provide insights about the user's financial health:

{data_summary}

Please provide:
1. Overall financial health assessment
2. Key strengths and areas for improvement
3. Specific recommendations for better financial wellness
4. Risk assessment and suggestions
5. Investment portfolio analysis (if applicable)

Be constructive and actionable in your recommendations."""
        
        return prompt
    
    async def generate_investment_insights(
        self,
        investment_data: Dict[str, Any],
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate investment insights using Gemini
        """
        try:
            logger.info("Generating investment insights")
            
            # Build investment analysis prompt
            analysis_prompt = self._build_investment_analysis_prompt(investment_data, market_data)
            
            # Generate insights
            insights_response = await self._generate_gemini_response(analysis_prompt)
            
            return {
                "success": True,
                "insights": insights_response,
                "analysis_date": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Investment insights generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "insights": "Unable to generate investment insights at this time."
            }
    
    def _build_investment_analysis_prompt(
        self,
        investment_data: Dict[str, Any],
        market_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build prompt for investment analysis
        """
        prompt = f"""{self.system_prompt}

Please analyze the following investment portfolio and provide insights:

Investment Portfolio:
{json.dumps(investment_data, indent=2)}

{f"Market Data: {json.dumps(market_data, indent=2)}" if market_data else ""}

Please provide:
1. Portfolio performance analysis
2. Risk assessment
3. Diversification analysis
4. Market timing insights
5. Specific recommendations for portfolio optimization
6. Long-term investment strategy suggestions

Focus on actionable insights and data-driven recommendations."""
        
        return prompt
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)