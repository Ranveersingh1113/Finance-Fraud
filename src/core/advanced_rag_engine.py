"""
Advanced RAG (Retrieval-Augmented Generation) engine for financial fraud detection.
Phase 2 implementation with production-grade models, re-ranking, and multi-stage retrieval.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from dataclasses import dataclass
import asyncio
import json

# Import for advanced models
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from FlagEmbedding import FlagReranker
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

if not any([ANTHROPIC_AVAILABLE, OLLAMA_AVAILABLE]):
    logging.warning("No LLM models available. Install anthropic or ollama for full functionality.")

try:
    from ..data.sebi_processor import ProcessedChunk
except ImportError:
    from data.sebi_processor import ProcessedChunk

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Enhanced query result with re-ranking scores and metadata."""
    document: str
    metadata: Dict[str, Any]
    similarity_score: float
    rerank_score: Optional[float] = None
    final_score: Optional[float] = None
    source: str = "unknown"


@dataclass
class RAGResponse:
    """Complete RAG response with generated answer and evidence."""
    query: str
    answer: str
    evidence: List[QueryResult]
    confidence_score: float
    query_type: str
    processing_time: float


class AdvancedRAGEngine:
    """
    Advanced RAG engine with production-grade models and multi-stage retrieval.
    
    Features:
    - Claude 3.5 Haiku or Ollama Llama 3.1 for generation (Model 2)
    - Fin-E5 fine-tuned embeddings (Model 4) - Coming soon
    - BGE reranker for post-retrieval ranking (Model 3)
    - Multi-stage query optimization
    - Real-time streaming capabilities
    - Local LLM support with Ollama
    """
    
    def __init__(self, persist_directory: str = "./data/chroma_db", 
                 anthropic_api_key: Optional[str] = None,
                 ollama_model: str = "llama3.1:8b",
                 ollama_host: str = "http://localhost:11434"):
        self.persist_directory = persist_directory
        
        # Initialize embedding model (upgrade to Fin-E5 when available)
        self.embedding_model = SentenceTransformer('all-MiniLM-L12-v2')
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collections
        self.transaction_collection = self.chroma_client.get_or_create_collection(
            name="transactions_advanced",
            metadata={"description": "IEEE-CIS transaction data with advanced features"}
        )
        
        self.sebi_collection = self.chroma_client.get_or_create_collection(
            name="sebi_documents_advanced",
            metadata={"description": "SEBI documents with advanced features"}
        )
        
        # Initialize advanced models
        self._initialize_advanced_models(anthropic_api_key, ollama_model, ollama_host)
        
        logger.info("Advanced RAG Engine initialized")
    
    def _initialize_advanced_models(self, anthropic_api_key: Optional[str] = None,
                                   ollama_model: str = "llama3.1:8b",
                                   ollama_host: str = "http://localhost:11434"):
        """Initialize advanced models for production use."""
        
        # Initialize LLM - Priority: Claude > Ollama > Fallback
        self.anthropic_client = None
        self.ollama_client = None
        self.use_claude = False
        self.use_ollama = False
        
        # Try Claude first if API key is provided
        if ANTHROPIC_AVAILABLE and anthropic_api_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
                self.use_claude = True
                logger.info("Claude 3.5 Haiku initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Claude: {e}")
        
        # Try Ollama if Claude is not available
        if not self.use_claude and OLLAMA_AVAILABLE:
            try:
                self.ollama_client = ollama.Client(host=ollama_host)
                # Test connection and model availability
                models = self.ollama_client.list()
                model_names = [model.model for model in models.models]
                
                if ollama_model in model_names:
                    self.use_ollama = True
                    self.ollama_model = ollama_model
                    logger.info(f"Ollama {ollama_model} initialized")
                else:
                    logger.warning(f"Ollama model {ollama_model} not found. Available models: {model_names}")
                    # Try to pull the model
                    logger.info(f"Attempting to pull {ollama_model}...")
                    self.ollama_client.pull(ollama_model)
                    self.use_ollama = True
                    self.ollama_model = ollama_model
                    logger.info(f"Successfully pulled and initialized {ollama_model}")
                    
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama: {e}")
        
        # Fallback warning
        if not self.use_claude and not self.use_ollama:
            logger.warning("No LLM available. Using fallback response generation.")
        
        # Initialize BGE Reranker (Model 3)
        if RERANKER_AVAILABLE:
            try:
                self.reranker = FlagReranker('BAAI/bge-reranker-large', use_fp16=True)
                self.use_reranker = True
                logger.info("BGE Reranker initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize BGE Reranker: {e}")
                self.reranker = None
                self.use_reranker = False
        else:
            self.reranker = None
            self.use_reranker = False
            logger.warning("BGE Reranker not available")
    
    def optimize_query(self, query: str) -> Dict[str, str]:
        """
        Multi-stage query optimization for better retrieval.
        
        Args:
            query: Original user query
            
        Returns:
            Dictionary with optimized query variations
        """
        try:
            # Basic query expansion
            expanded_queries = {
                'original': query,
                'expanded': self._expand_query(query),
                'technical': self._technical_query(query),
                'contextual': self._contextual_query(query)
            }
            
            return expanded_queries
            
        except Exception as e:
            logger.error(f"Error optimizing query: {e}")
            return {'original': query}
    
    def _expand_query(self, query: str) -> str:
        """Expand query with related financial fraud terms."""
        fraud_terms = {
            'fraud': ['scam', 'deception', 'manipulation', 'misrepresentation'],
            'insider': ['insider trading', 'material non-public information', 'tipping'],
            'market': ['market manipulation', 'price rigging', 'wash trading'],
            'money': ['money laundering', 'layering', 'integration', 'placement']
        }
        
        expanded = query.lower()
        for term, synonyms in fraud_terms.items():
            if term in expanded:
                expanded += f" {' '.join(synonyms)}"
        
        return expanded
    
    def _technical_query(self, query: str) -> str:
        """Create technical query with regulatory terminology."""
        technical_mapping = {
            'fraud': 'securities fraud violation',
            'insider trading': 'violation of SEBI (Prohibition of Insider Trading) Regulations',
            'market manipulation': 'fraudulent and unfair trade practices',
            'penalty': 'monetary penalty disgorgement prohibition'
        }
        
        technical_query = query.lower()
        for term, technical in technical_mapping.items():
            if term in technical_query:
                technical_query = technical_query.replace(term, technical)
        
        return technical_query
    
    def _contextual_query(self, query: str) -> str:
        """Create contextual query with SEBI-specific context."""
        contextual_additions = [
            "SEBI enforcement action",
            "securities market violation",
            "regulatory penalty"
        ]
        
        return f"{query} {' '.join(contextual_additions)}"
    
    def multi_stage_retrieval(self, query: str, n_results: int = 10) -> List[QueryResult]:
        """
        Multi-stage retrieval with query optimization and re-ranking.
        
        Args:
            query: User query
            n_results: Number of final results to return
            
        Returns:
            List of QueryResult objects with final scores
        """
        try:
            # Stage 1: Query optimization
            optimized_queries = self.optimize_query(query)
            
            # Stage 2: Initial retrieval from all query variations
            all_results = []
            for query_type, optimized_query in optimized_queries.items():
                # Search both collections
                transaction_results = self._search_transactions_advanced(optimized_query, n_results * 2)
                sebi_results = self._search_sebi_documents_advanced(optimized_query, n_results * 2)
                
                # Add query type to results
                for result in transaction_results:
                    result.source = "transactions"
                    result.query_type = query_type
                for result in sebi_results:
                    result.source = "sebi_documents"
                    result.query_type = query_type
                
                all_results.extend(transaction_results + sebi_results)
            
            # Stage 3: Deduplicate results
            unique_results = self._deduplicate_results(all_results)
            
            # Stage 4: Re-ranking (if available)
            if self.use_reranker and len(unique_results) > 1:
                reranked_results = self._rerank_results(query, unique_results)
            else:
                reranked_results = unique_results
            
            # Stage 5: Final scoring and selection
            final_results = self._calculate_final_scores(query, reranked_results)
            final_results = sorted(final_results, key=lambda x: x.final_score, reverse=True)
            
            return final_results[:n_results]
            
        except Exception as e:
            logger.error(f"Error in multi-stage retrieval: {e}")
            return []
    
    def _search_transactions_advanced(self, query: str, n_results: int) -> List[QueryResult]:
        """Advanced transaction search with enhanced metadata."""
        try:
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            results = self.transaction_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            query_results = []
            for i in range(len(results['documents'][0])):
                query_results.append(QueryResult(
                    document=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    similarity_score=1 - results['distances'][0][i]
                ))
            
            return query_results
            
        except Exception as e:
            logger.error(f"Error searching transactions: {e}")
            return []
    
    def _search_sebi_documents_advanced(self, query: str, n_results: int) -> List[QueryResult]:
        """Advanced SEBI document search with filtering and enhanced metadata."""
        try:
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            results = self.sebi_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            query_results = []
            for i in range(len(results['documents'][0])):
                query_results.append(QueryResult(
                    document=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    similarity_score=1 - results['distances'][0][i]
                ))
            
            return query_results
            
        except Exception as e:
            logger.error(f"Error searching SEBI documents: {e}")
            return []
    
    def _deduplicate_results(self, results: List[QueryResult]) -> List[QueryResult]:
        """Remove duplicate results based on document content."""
        seen_docs = set()
        unique_results = []
        
        for result in results:
            doc_hash = hash(result.document[:100])  # Use first 100 chars as fingerprint
            if doc_hash not in seen_docs:
                seen_docs.add(doc_hash)
                unique_results.append(result)
        
        return unique_results
    
    def _rerank_results(self, query: str, results: List[QueryResult]) -> List[QueryResult]:
        """Re-rank results using BGE reranker."""
        try:
            if not results:
                return results
            
            # Prepare query-document pairs for reranking
            query_doc_pairs = [(query, result.document) for result in results]
            
            # Get rerank scores
            rerank_scores = self.reranker.compute_score(query_doc_pairs)
            
            # Update results with rerank scores
            for i, result in enumerate(results):
                if isinstance(rerank_scores, list):
                    result.rerank_score = rerank_scores[i]
                else:
                    result.rerank_score = rerank_scores
            
            return results
            
        except Exception as e:
            logger.error(f"Error reranking results: {e}")
            return results
    
    def _calculate_final_scores(self, query: str, results: List[QueryResult]) -> List[QueryResult]:
        """Calculate final scores combining similarity and rerank scores."""
        for result in results:
            # Base similarity score
            similarity_weight = 0.4
            similarity_score = result.similarity_score * similarity_weight
            
            # Rerank score (if available)
            rerank_weight = 0.6
            if result.rerank_score is not None:
                # Normalize rerank score to 0-1 range
                normalized_rerank = min(max(result.rerank_score, 0), 1)
                rerank_score = normalized_rerank * rerank_weight
            else:
                rerank_score = similarity_score * rerank_weight
            
            # Combine scores
            result.final_score = similarity_score + rerank_score
        
        return results
    
    async def generate_answer(self, query: str, evidence: List[QueryResult]) -> str:
        """
        Generate answer using Claude 3.5 Haiku, Ollama, or fallback LLM.
        
        Args:
            query: User query
            evidence: Retrieved evidence documents
            
        Returns:
            Generated answer
        """
        try:
            if self.use_claude and self.anthropic_client:
                return await self._generate_with_claude(query, evidence)
            elif self.use_ollama and self.ollama_client:
                return await self._generate_with_ollama(query, evidence)
            else:
                return self._generate_fallback_answer(query, evidence)
                
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return "I apologize, but I encountered an error while generating a response. Please try again."
    
    async def _generate_with_claude(self, query: str, evidence: List[QueryResult]) -> str:
        """Generate answer using Claude 3.5 Haiku."""
        try:
            # Prepare context from evidence
            context = "\n\n".join([
                f"Document {i+1}:\n{result.document[:1000]}..."
                for i, result in enumerate(evidence[:5])  # Use top 5 evidence
            ])
            
            # Create prompt
            prompt = f"""You are a financial fraud detection expert analyzing SEBI enforcement actions and transaction patterns. 
            
            Based on the following evidence, provide a comprehensive answer to the user's question about financial fraud patterns, regulatory violations, or enforcement actions.

            Evidence:
            {context}

            Question: {query}

            Please provide:
            1. A direct answer to the question
            2. Specific examples from the evidence
            3. Relevant regulatory context
            4. Any patterns or trends you identify

            Keep your response clear, factual, and well-structured."""

            # Generate response
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error with Claude generation: {e}")
            return self._generate_fallback_answer(query, evidence)
    
    async def _generate_with_ollama(self, query: str, evidence: List[QueryResult]) -> str:
        """Generate answer using Ollama with Llama 3.1."""
        try:
            # Prepare context from evidence
            context = "\n\n".join([
                f"Document {i+1}:\n{result.document[:1000]}..."
                for i, result in enumerate(evidence[:5])  # Use top 5 evidence
            ])
            
            # Create prompt optimized for Llama 3.1
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a financial fraud detection expert analyzing SEBI enforcement actions and transaction patterns. You provide comprehensive, factual analysis based on regulatory documents and enforcement data.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Based on the following evidence from SEBI enforcement documents, provide a detailed answer to the user's question about financial fraud patterns, regulatory violations, or enforcement actions.

Evidence:
{context}

Question: {query}

Please provide:
1. A direct answer to the question
2. Specific examples from the evidence with relevant details
3. Regulatory context and compliance requirements
4. Patterns or trends you identify
5. Key entities and violation types mentioned

Keep your response clear, factual, well-structured, and cite specific examples from the evidence.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

            # Generate response using Ollama
            response = self.ollama_client.chat(
                model=self.ollama_model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.3,  # Lower temperature for more factual responses
                    'top_p': 0.9,
                    'max_tokens': 2048
                }
            )
            
            return response['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"Error with Ollama generation: {e}")
            return self._generate_fallback_answer(query, evidence)
    
    def _generate_fallback_answer(self, query: str, evidence: List[QueryResult]) -> str:
        """Fallback answer generation when Claude is not available."""
        if not evidence:
            return "I couldn't find relevant information to answer your question. Please try rephrasing your query."
        
        # Simple template-based response
        top_evidence = evidence[0]
        
        answer = f"Based on the available evidence, here's what I found:\n\n"
        answer += f"**Query**: {query}\n\n"
        answer += f"**Most Relevant Document**: {top_evidence.document[:500]}...\n\n"
        
        if len(evidence) > 1:
            answer += f"**Additional Evidence**: Found {len(evidence)-1} more relevant documents.\n"
        
        answer += f"**Confidence**: {top_evidence.final_score:.2f}\n"
        
        return answer
    
    async def query(self, query: str, n_results: int = 10) -> RAGResponse:
        """
        Complete RAG query with retrieval and generation.
        
        Args:
            query: User query
            n_results: Number of evidence documents to retrieve
            
        Returns:
            Complete RAG response
        """
        import time
        start_time = time.time()
        
        try:
            # Multi-stage retrieval
            evidence = self.multi_stage_retrieval(query, n_results)
            
            # Generate answer
            answer = await self.generate_answer(query, evidence)
            
            # Calculate confidence
            confidence = self._calculate_confidence(evidence)
            
            # Determine query type
            query_type = self._classify_query_type(query)
            
            processing_time = time.time() - start_time
            
            return RAGResponse(
                query=query,
                answer=answer,
                evidence=evidence,
                confidence_score=confidence,
                query_type=query_type,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            processing_time = time.time() - start_time
            return RAGResponse(
                query=query,
                answer="I encountered an error while processing your query.",
                evidence=[],
                confidence_score=0.0,
                query_type="error",
                processing_time=processing_time
            )
    
    def _calculate_confidence(self, evidence: List[QueryResult]) -> float:
        """Calculate confidence score based on evidence quality."""
        if not evidence:
            return 0.0
        
        # Average final score of top evidence
        top_scores = [result.final_score for result in evidence[:3] if result.final_score]
        if not top_scores:
            return 0.0
        
        return sum(top_scores) / len(top_scores)
    
    def _classify_query_type(self, query: str) -> str:
        """Classify query type for better handling."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['insider', 'tipping', 'material']):
            return "insider_trading"
        elif any(word in query_lower for word in ['manipulation', 'rigging', 'wash']):
            return "market_manipulation"
        elif any(word in query_lower for word in ['penalty', 'fine', 'disgorgement']):
            return "enforcement_action"
        elif any(word in query_lower for word in ['company', 'entity', 'person']):
            return "entity_inquiry"
        else:
            return "general_fraud"
    
    # Inherit collection management methods from BaselineRAGEngine
    def add_sebi_chunks(self, chunks: List[ProcessedChunk]) -> None:
        """Add processed SEBI chunks to the advanced vector database."""
        try:
            if not chunks:
                logger.warning("No SEBI chunks to add")
                return
            
            # Prepare documents
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                documents.append(chunk.content)
                
                # Enhanced metadata for advanced features (ensure no None values)
                metadata = {
                    'chunk_id': chunk.chunk_id or '',
                    'document_id': chunk.document_id or '',
                    'document_type': chunk.document_type or 'unknown',
                    'title': chunk.title or '',
                    'chunk_index': chunk.chunk_index or 0,
                    'violation_types': ', '.join(chunk.violation_types) if chunk.violation_types else '',
                    'entities': ', '.join(chunk.entities) if chunk.entities else '',
                    'keywords': ', '.join(chunk.keywords) if chunk.keywords else '',
                    'source': 'sebi_processed_advanced',
                    'content_length': len(chunk.content) if chunk.content else 0,
                    'word_count': chunk.metadata.get('chunk_word_count', 0) or 0,
                    'date': str(chunk.date) if chunk.date else '',
                    'url': chunk.url or ''
                }
                
                # Add all document metadata (filter out None values)
                for key, value in chunk.metadata.items():
                    if value is not None and isinstance(value, (str, int, float, bool)):
                        metadata[f"doc_{key}"] = value
                
                metadatas.append(metadata)
                ids.append(chunk.chunk_id)
            
            # Generate embeddings and add to collection
            embeddings = self.embedding_model.encode(documents).tolist()
            
            self.sebi_collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} processed SEBI chunks to advanced vector database")
            
        except Exception as e:
            logger.error(f"Error adding SEBI chunks: {e}")
            raise
    
    def get_advanced_stats(self) -> Dict[str, Any]:
        """Get advanced statistics about the vector database."""
        try:
            transaction_count = self.transaction_collection.count()
            sebi_count = self.sebi_collection.count()
            
            return {
                'transaction_count': transaction_count,
                'sebi_document_count': sebi_count,
                'total_documents': transaction_count + sebi_count,
                'models_available': {
                    'claude_3_5_haiku': self.use_claude,
                    'ollama_llama': self.use_ollama,
                    'bge_reranker': self.use_reranker,
                    'embedding_model': 'all-MiniLM-L12-v2'
                },
                'advanced_features': {
                    'query_optimization': True,
                    'multi_stage_retrieval': True,
                    'reranking': self.use_reranker,
                    'confidence_scoring': True
                }
            }
        except Exception as e:
            logger.error(f"Error getting advanced stats: {e}")
            return {'error': str(e)}
