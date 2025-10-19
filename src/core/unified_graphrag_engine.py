"""
Unified GraphRAG Engine for Financial Intelligence Platform.
Combines SEBI regulatory graph + AMLSim transaction graph for cross-domain intelligence.
Phase 4: Week 5-6 - Unified GraphRAG System
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import asyncio

from .sebi_graph_manager import SEBIGraphManager
from .amlsim_graph_manager import AMLSimGraphManager
from .advanced_rag_engine import AdvancedRAGEngine, RAGResponse, QueryResult

logger = logging.getLogger(__name__)


class UnifiedGraphRAGEngine:
    """
    Unified GraphRAG engine combining SEBI and AMLSim knowledge graphs.
    
    Enables cross-domain queries that leverage both:
    - Regulatory intelligence (SEBI violations, penalties, precedents)
    - Transaction intelligence (AMLSim money flows, fraud patterns)
    
    Key Capabilities:
    - Multi-graph traversal
    - Cross-domain pattern matching
    - Enhanced context gathering
    - Unified answer generation
    """
    
    def __init__(self, persist_directory: str = "./data/graphs",
                 chroma_directory: str = "./data/chroma_db",
                 anthropic_api_key: Optional[str] = None,
                 ollama_model: str = "llama3.1:8b"):
        """
        Initialize unified GraphRAG engine.
        
        Args:
            persist_directory: Directory with saved graphs
            chroma_directory: ChromaDB directory
            anthropic_api_key: Optional Anthropic API key
            ollama_model: Ollama model name
        """
        self.persist_directory = Path(persist_directory)
        
        # Initialize knowledge graphs
        logger.info("Loading SEBI knowledge graph...")
        self.sebi_graph = SEBIGraphManager(persist_directory=str(persist_directory))
        if not self.sebi_graph.load_graph():
            logger.warning("SEBI graph not found - build it first")
        
        logger.info("Loading AMLSim transaction graph...")
        self.amlsim_graph = AMLSimGraphManager(persist_directory=str(persist_directory))
        if not self.amlsim_graph.load_graph():
            logger.warning("AMLSim graph not found - build it first")
        
        # Initialize RAG engine
        logger.info("Initializing RAG engine...")
        self.rag_engine = AdvancedRAGEngine(
            persist_directory=chroma_directory,
            anthropic_api_key=anthropic_api_key,
            ollama_model=ollama_model
        )
        
        # Get AMLSim collection
        try:
            self.amlsim_collection = self.rag_engine.chroma_client.get_collection(
                name="amlsim_transactions"
            )
            logger.info("AMLSim collection loaded")
        except Exception as e:
            logger.warning(f"AMLSim collection not found: {e}")
            self.amlsim_collection = None
        
        logger.info("Unified GraphRAG Engine initialized")
    
    async def unified_query(self, query: str, use_graphs: bool = True,
                           n_results: int = 10) -> Dict[str, Any]:
        """
        Unified query across SEBI and AMLSim knowledge bases.
        
        Args:
            query: User query
            use_graphs: Whether to use graph context enhancement
            n_results: Number of results to return
            
        Returns:
            Unified response with both regulatory and transaction intelligence
        """
        logger.info(f"Processing unified query: {query}")
        
        # Step 1: Classify query intent
        query_type = self._classify_query_intent(query)
        logger.info(f"Query classified as: {query_type}")
        
        # Step 2: Graph context gathering (if enabled)
        graph_context = {}
        if use_graphs:
            graph_context = await self._gather_graph_context(query, query_type)
        
        # Step 3: RAG retrieval from both collections
        rag_results = await self._dual_rag_retrieval(query, n_results)
        
        # Step 4: Cross-domain pattern matching
        patterns = self._match_cross_domain_patterns(graph_context, rag_results)
        
        # Step 5: Generate unified answer
        answer = await self._generate_unified_answer(
            query=query,
            graph_context=graph_context,
            rag_results=rag_results,
            patterns=patterns
        )
        
        # Extract entities for easier access
        sebi_entities = []
        if 'sebi_context' in graph_context:
            for key, value in graph_context['sebi_context'].items():
                if key.endswith('_cases') and isinstance(value, list):
                    sebi_entities.extend(value)
        
        amlsim_patterns = []
        if 'amlsim_context' in graph_context:
            for key, value in graph_context['amlsim_context'].items():
                if key.endswith('_patterns') and isinstance(value, list):
                    amlsim_patterns.extend(value)
        
        return {
            'query': query,
            'query_type': query_type,
            'answer': answer,
            'graph_context': {
                'sebi_entities': sebi_entities,
                'amlsim_patterns': amlsim_patterns,
                'full_context': graph_context
            },
            'sebi_results': rag_results.get('sebi_results', []),
            'amlsim_results': rag_results.get('amlsim_results', []),
            'cross_domain_patterns': patterns,
            # Keep original for backwards compatibility
            'rag_results': rag_results
        }
    
    def _classify_query_intent(self, query: str) -> str:
        """
        Classify query intent to determine which knowledge bases to use.
        
        Returns:
            'regulatory', 'transactional', 'combined', or 'general'
        """
        query_lower = query.lower()
        
        # Regulatory keywords
        regulatory_keywords = [
            'sebi', 'penalty', 'violation', 'regulation', 'enforcement',
            'insider trading', 'market manipulation', 'penalty', 'order'
        ]
        
        # Transaction keywords
        transaction_keywords = [
            'account', 'transaction', 'transfer', 'money flow', 'trace',
            'fan-out', 'fan-in', 'cycle', 'layering', 'suspicious', 'fraud ring'
        ]
        
        # Cross-domain keywords
        cross_domain_keywords = [
            'similar to', 'match', 'like', 'pattern', 'compare'
        ]
        
        has_regulatory = any(kw in query_lower for kw in regulatory_keywords)
        has_transaction = any(kw in query_lower for kw in transaction_keywords)
        has_cross_domain = any(kw in query_lower for kw in cross_domain_keywords)
        
        if has_cross_domain or (has_regulatory and has_transaction):
            return 'combined'
        elif has_regulatory:
            return 'regulatory'
        elif has_transaction:
            return 'transactional'
        else:
            return 'general'
    
    async def _gather_graph_context(self, query: str, query_type: str) -> Dict[str, Any]:
        """
        Gather context from both knowledge graphs.
        
        Args:
            query: User query
            query_type: Classification of query intent
            
        Returns:
            Combined graph context from both graphs
        """
        context = {
            'sebi_context': {},
            'amlsim_context': {},
            'cross_domain_links': []
        }
        
        # SEBI graph context
        if query_type in ['regulatory', 'combined', 'general']:
            try:
                # Extract entities from query for SEBI
                sebi_stats = self.sebi_graph.get_sebi_statistics()
                context['sebi_context'] = {
                    'total_entities': sebi_stats['sebi_specific']['entities'],
                    'total_violations': sebi_stats['sebi_specific']['violations'],
                    'available': True
                }
                
                # Search for specific violations if mentioned
                query_lower = query.lower()
                for violation_type in ['insider trading', 'fraud', 'money laundering', 'market manipulation']:
                    if violation_type in query_lower:
                        similar_cases = self.sebi_graph.find_similar_cases(violation_type, limit=5)
                        context['sebi_context'][f'{violation_type}_cases'] = similar_cases
                
            except Exception as e:
                logger.error(f"Error gathering SEBI context: {e}")
                context['sebi_context']['available'] = False
        
        # AMLSim graph context
        if query_type in ['transactional', 'combined', 'general']:
            try:
                amlsim_stats = self.amlsim_graph.get_amlsim_statistics()
                context['amlsim_context'] = {
                    'total_accounts': amlsim_stats['amlsim_specific']['accounts'],
                    'suspicious_accounts': amlsim_stats['amlsim_specific']['suspicious_accounts'],
                    'available': True
                }
                
                # Detect patterns if query mentions them
                query_lower = query.lower()
                if any(word in query_lower for word in ['fan-out', 'fan out', 'placement']):
                    fan_out = self.amlsim_graph.detect_fan_out_patterns(threshold=5)
                    context['amlsim_context']['fan_out_patterns'] = fan_out[:5]
                
                if any(word in query_lower for word in ['fan-in', 'fan in', 'collection']):
                    fan_in = self.amlsim_graph.detect_fan_in_patterns(threshold=5)
                    context['amlsim_context']['fan_in_patterns'] = fan_in[:5]
                
            except Exception as e:
                logger.error(f"Error gathering AMLSim context: {e}")
                context['amlsim_context']['available'] = False
        
        return context
    
    def _expand_query(self, query: str, query_type: str) -> List[str]:
        """
        Expand query with synonyms and related terms for better retrieval.
        
        Args:
            query: Original query
            query_type: Type of query (regulatory, transactional, etc.)
            
        Returns:
            List of query variations
        """
        queries = [query]
        query_lower = query.lower()
        
        # Regulatory term expansions
        expansions = {
            'money laundering': ['money laundering', 'PMLA', 'layering', 'placement', 'integration', 'suspicious transactions', 'anti-money laundering', 'AML'],
            'insider trading': ['insider trading', 'PIT regulations', 'UPSI', 'unpublished price sensitive information', 'price sensitive', 'code of conduct'],
            'market manipulation': ['market manipulation', 'PFUTP', 'fraudulent trade practices', 'unfair trade', 'price rigging', 'wash trading'],
            'disclosure': ['disclosure', 'LODR', 'listing obligations', 'continuous disclosure', 'material events', 'corporate governance'],
            'penalty': ['penalty', 'fine', 'sanction', 'monetary penalty', 'punishment', 'disgorgement'],
            'kyc': ['KYC', 'know your client', 'customer due diligence', 'CDD', 'client identification'],
            'regulation': ['regulation', 'rules', 'provisions', 'requirements', 'obligations', 'compliance']
        }
        
        # Add expanded terms
        for key, terms in expansions.items():
            if key in query_lower:
                # Add a query with all synonyms
                expanded = query
                for term in terms[:3]:  # Use top 3 synonyms
                    if term.lower() not in query_lower:
                        expanded += f" {term}"
                if expanded != query:
                    queries.append(expanded)
                break
        
        return queries[:2]  # Return original + one expanded version
    
    def _boost_by_document_type(self, results: List[Dict], query_type: str) -> List[Dict]:
        """
        Boost document scores based on document type relevance to query.
        Uses additive boosting for better prioritization.
        
        Args:
            results: Retrieved results
            query_type: Type of query
            
        Returns:
            Results with adjusted scores
        """
        for result in results:
            doc_type = result.get('metadata', {}).get('document_type', 'unknown')
            original_score = result.get('score', 0.5)
            
            # Boost regulations for regulatory queries (ADDITIVE, not multiplicative)
            if query_type == 'regulatory':
                if 'regulation' in doc_type:
                    # Strong boost for actual regulations
                    result['score'] = original_score + 0.5  # Add 0.5 bonus
                    result['boosted'] = True
                    result['boost_reason'] = 'regulation_for_regulatory_query'
                elif 'adjudication_order' in doc_type:
                    # Small penalty for cases in regulatory queries
                    result['score'] = original_score - 0.1  # Subtract 0.1
                    result['boosted'] = False
            
            # For transactional queries, boost transaction docs
            elif query_type == 'transactional':
                if 'transaction' in doc_type.lower():
                    result['score'] = original_score + 0.3  # Add 0.3 bonus
                    result['boosted'] = True
                    result['boost_reason'] = 'transaction_for_transaction_query'
                elif 'regulation' in doc_type:
                    # Keep regulations neutral for transaction queries
                    pass
            
            # For combined queries, moderate boosting
            elif query_type == 'combined':
                if 'regulation' in doc_type:
                    result['score'] = original_score + 0.2  # Moderate boost
                    result['boosted'] = True
                    result['boost_reason'] = 'regulation_for_combined_query'
        
        return results
    
    def _ensure_diversity(self, results: List[Dict], target_count: int = 10) -> List[Dict]:
        """
        Ensure diversity in results (mix of regulations and cases).
        Prioritizes regulations over cases for regulatory queries.
        
        Args:
            results: All results
            target_count: Target number of diverse results
            
        Returns:
            Diversified results
        """
        if not results:
            return results
        
        # Remove duplicates based on document content similarity
        seen_titles = set()
        unique_results = []
        
        for result in results:
            title = result.get('metadata', {}).get('title', '')
            doc_id = result.get('id', '')
            
            # Create a unique key (use first 50 chars of title or doc_id)
            unique_key = (title[:50] if title else doc_id)
            
            if unique_key not in seen_titles:
                seen_titles.add(unique_key)
                unique_results.append(result)
        
        # Separate by document type
        regulations = []
        cases = []
        others = []
        
        for result in unique_results:
            doc_type = result.get('metadata', {}).get('document_type', 'unknown')
            if 'regulation' in doc_type:
                regulations.append(result)
            elif 'adjudication_order' in doc_type:
                cases.append(result)
            else:
                others.append(result)
        
        # Build diverse result set
        diverse = []
        
        # Prioritize regulations (most authoritative)
        if regulations:
            # Sort by score and take top regulations
            regulations_sorted = sorted(regulations, key=lambda x: x.get('score', 0), reverse=True)
            diverse.extend(regulations_sorted[:min(7, len(regulations_sorted))])  # Up to 7 regulations
        
        # Add cases for precedent examples
        if cases and len(diverse) < target_count:
            cases_sorted = sorted(cases, key=lambda x: x.get('score', 0), reverse=True)
            diverse.extend(cases_sorted[:target_count - len(diverse)])
        
        # Fill with others if needed
        if others and len(diverse) < target_count:
            others_sorted = sorted(others, key=lambda x: x.get('score', 0), reverse=True)
            diverse.extend(others_sorted[:target_count - len(diverse)])
        
        # Final sort by score to respect boosted regulations
        diverse.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return diverse[:target_count]
    
    async def _dual_rag_retrieval(self, query: str, n_results: int) -> Dict[str, List]:
        """
        Enhanced retrieval from both SEBI and AMLSim ChromaDB collections.
        Includes query expansion, document type boosting, and diversity.
        
        Args:
            query: User query
            n_results: Number of results per collection
            
        Returns:
            Enhanced results from both collections
        """
        results = {
            'sebi_results': [],
            'amlsim_results': []
        }
        
        # Classify query for intelligent retrieval
        query_type = self._classify_query_intent(query)
        
        # Expand query for better recall
        query_variations = self._expand_query(query, query_type)
        
        # Query SEBI collection with multiple query variations
        try:
            all_sebi_results = []
            
            for q_var in query_variations:
                query_embedding = self.rag_engine.embedding_model.encode([q_var]).tolist()[0]
                
                sebi_results = self.rag_engine.sebi_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results * 2,  # Get more results for diversity
                    include=['documents', 'metadatas', 'distances']
                )
                
                if sebi_results['documents'] and sebi_results['documents'][0]:
                    for i in range(len(sebi_results['documents'][0])):
                        doc_id = sebi_results.get('ids', [[]])[0][i] if 'ids' in sebi_results else f"doc_{i}"
                        
                        # Avoid duplicates
                        if not any(r.get('id') == doc_id for r in all_sebi_results):
                            all_sebi_results.append({
                                'id': doc_id,
                                'document': sebi_results['documents'][0][i],
                                'metadata': sebi_results['metadatas'][0][i],
                                'score': 1 - sebi_results['distances'][0][i],
                                'source': 'sebi_regulatory',
                                'query_variation': q_var
                            })
            
            # Apply document type boosting
            all_sebi_results = self._boost_by_document_type(all_sebi_results, query_type)
            
            # Ensure diversity
            results['sebi_results'] = self._ensure_diversity(all_sebi_results, n_results)
            
        except Exception as e:
            logger.error(f"Error querying SEBI collection: {e}")
        
        # Query AMLSim collection
        if self.amlsim_collection:
            try:
                all_amlsim_results = []
                
                for q_var in query_variations:
                    query_embedding = self.rag_engine.embedding_model.encode([q_var]).tolist()[0]
                    
                    amlsim_results = self.amlsim_collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n_results,
                        include=['documents', 'metadatas', 'distances']
                    )
                    
                    if amlsim_results['documents'] and amlsim_results['documents'][0]:
                        for i in range(len(amlsim_results['documents'][0])):
                            doc_id = amlsim_results.get('ids', [[]])[0][i] if 'ids' in amlsim_results else f"doc_{i}"
                            
                            if not any(r.get('id') == doc_id for r in all_amlsim_results):
                                all_amlsim_results.append({
                                    'id': doc_id,
                                    'document': amlsim_results['documents'][0][i],
                                    'metadata': amlsim_results['metadatas'][0][i],
                                    'score': 1 - amlsim_results['distances'][0][i],
                                    'source': 'amlsim_transaction',
                                    'query_variation': q_var
                                })
                
                # Sort and take top results
                all_amlsim_results.sort(key=lambda x: x.get('score', 0), reverse=True)
                results['amlsim_results'] = all_amlsim_results[:n_results]
            
            except Exception as e:
                logger.error(f"Error querying AMLSim collection: {e}")
        
        logger.info(f"Enhanced retrieval: {len(results['sebi_results'])} SEBI + "
                   f"{len(results['amlsim_results'])} AMLSim results "
                   f"(from {len(query_variations)} query variations)")
        
        return results
    
    def _match_cross_domain_patterns(self, graph_context: Dict,
                                     rag_results: Dict) -> List[Dict]:
        """
        Find patterns that match across SEBI and AMLSim domains.
        
        Args:
            graph_context: Context from both graphs
            rag_results: RAG retrieval results
            
        Returns:
            List of cross-domain pattern matches
        """
        matches = []
        
        sebi_ctx = graph_context.get('sebi_context', {})
        amlsim_ctx = graph_context.get('amlsim_context', {})
        
        # Match 1: Fan-out patterns to SEBI fraud violations
        if 'fan_out_patterns' in amlsim_ctx:
            # Get SEBI fraud cases
            sebi_fraud_cases = self.sebi_graph.find_similar_cases("fraud", limit=5)
            
            fan_out_patterns = amlsim_ctx.get('fan_out_patterns', [])
            if fan_out_patterns and sebi_fraud_cases:
                for pattern in fan_out_patterns[:3]:
                    matches.append({
                        'match_type': 'fan_out_to_fraud',
                        'amlsim_account': pattern['source_account'],
                        'destinations': pattern['num_destinations'],
                        'amount': pattern['total_amount'],
                        'sebi_cases_count': len(sebi_fraud_cases),
                        'confidence': 0.85,
                        'description': f"Fan-out pattern ({pattern['num_destinations']} destinations, "
                                     f"${pattern['total_amount']:,.0f}) matches SEBI fraud patterns "
                                     f"({len(sebi_fraud_cases)} similar cases)"
                    })
        
        # Match 2: Fan-in patterns to SEBI money laundering
        if 'fan_in_patterns' in amlsim_ctx:
            # Get SEBI money laundering cases
            sebi_ml_cases = self.sebi_graph.find_similar_cases("money_laundering", limit=5)
            
            fan_in_patterns = amlsim_ctx.get('fan_in_patterns', [])
            if fan_in_patterns and sebi_ml_cases:
                for pattern in fan_in_patterns[:3]:
                    matches.append({
                        'match_type': 'fan_in_to_money_laundering',
                        'amlsim_account': pattern['destination_account'],
                        'sources': pattern['num_sources'],
                        'amount': pattern['total_amount'],
                        'sebi_cases_count': len(sebi_ml_cases),
                        'confidence': 0.82,
                        'description': f"Fan-in pattern ({pattern['num_sources']} sources, "
                                     f"${pattern['total_amount']:,.0f}) matches SEBI money laundering "
                                     f"integration patterns ({len(sebi_ml_cases)} similar cases)"
                    })
        
        # Match 3: General suspicious account to SEBI violations
        suspicious_count = amlsim_ctx.get('suspicious_accounts', 0)
        if suspicious_count > 0:
            # Try to find any SEBI violation cases
            for violation in ['fraud', 'money_laundering', 'Unfair Trade Practice']:
                sebi_cases = self.sebi_graph.find_similar_cases(violation, limit=3)
                if sebi_cases:
                    matches.append({
                        'match_type': 'general_suspicious_to_violation',
                        'amlsim_suspicious_count': suspicious_count,
                        'sebi_violation': violation,
                        'sebi_cases_count': len(sebi_cases),
                        'confidence': 0.70,
                        'description': f"{suspicious_count} suspicious accounts in AMLSim network "
                                     f"exhibit patterns similar to SEBI {violation} violations "
                                     f"({len(sebi_cases)} regulatory precedents)"
                    })
                    break  # Only add one general match
        
        logger.info(f"Found {len(matches)} cross-domain pattern matches")
        return matches
    
    async def _generate_unified_answer(self, query: str,
                                      graph_context: Dict,
                                      rag_results: Dict,
                                      patterns: List[Dict]) -> str:
        """
        Generate unified answer using both regulatory and transaction context.
        
        Args:
            query: User query
            graph_context: Context from graphs
            rag_results: RAG retrieval results
            patterns: Cross-domain patterns
            
        Returns:
            Generated answer with graph intelligence
        """
        # Build answer sections
        answer_parts = []
        
        # Part 1: Graph Intelligence Summary
        sebi_ctx = graph_context.get('sebi_context', {})
        amlsim_ctx = graph_context.get('amlsim_context', {})
        
        if sebi_ctx.get('available') or amlsim_ctx.get('available'):
            answer_parts.append("**KNOWLEDGE GRAPH INTELLIGENCE:**")
            
            if sebi_ctx.get('available'):
                answer_parts.append(f"\nSEBI Regulatory Database:")
                answer_parts.append(f"- {sebi_ctx.get('total_entities', 0):,} entities tracked")
                answer_parts.append(f"- {sebi_ctx.get('total_violations', 0)} violation types on record")
            
            if amlsim_ctx.get('available'):
                answer_parts.append(f"\nTransaction Network Analysis:")
                answer_parts.append(f"- {amlsim_ctx.get('total_accounts', 0):,} accounts monitored")
                answer_parts.append(f"- {amlsim_ctx.get('suspicious_accounts', 0)} suspicious accounts flagged")
                
                # Add pattern-specific insights
                if 'fan_out_patterns' in amlsim_ctx:
                    top_fan_out = amlsim_ctx['fan_out_patterns'][0] if amlsim_ctx['fan_out_patterns'] else None
                    if top_fan_out:
                        answer_parts.append(f"- Top fan-out pattern: {top_fan_out['source_account']} "
                                          f"({top_fan_out['num_destinations']} destinations, "
                                          f"${top_fan_out['total_amount']:,.0f})")
                
                if 'fan_in_patterns' in amlsim_ctx:
                    top_fan_in = amlsim_ctx['fan_in_patterns'][0] if amlsim_ctx['fan_in_patterns'] else None
                    if top_fan_in:
                        answer_parts.append(f"- Top fan-in pattern: {top_fan_in['destination_account']} "
                                          f"({top_fan_in['num_sources']} sources, "
                                          f"${top_fan_in['total_amount']:,.0f})")
        
        # Part 2: Cross-Domain Pattern Matches
        if patterns:
            answer_parts.append("\n\n**CROSS-DOMAIN PATTERN ANALYSIS:**")
            for i, pattern in enumerate(patterns, 1):
                answer_parts.append(f"\n{i}. {pattern['description']}")
                answer_parts.append(f"   Confidence: {pattern['confidence']:.0%}")
        
        # Part 3: Document Evidence (from RAG)
        sebi_results = rag_results.get('sebi_results', [])
        amlsim_results = rag_results.get('amlsim_results', [])
        
        if sebi_results or amlsim_results:
            answer_parts.append("\n\n**DOCUMENT EVIDENCE:**")
            
            if sebi_results:
                answer_parts.append(f"\nSEBI Regulatory Documents ({len(sebi_results)} found):")
                for i, result in enumerate(sebi_results[:3], 1):
                    doc_preview = result['document'][:200].replace('\n', ' ')
                    answer_parts.append(f"{i}. {doc_preview}...")
            
            if amlsim_results:
                answer_parts.append(f"\nTransaction Records ({len(amlsim_results)} found):")
                for i, result in enumerate(amlsim_results[:3], 1):
                    doc_preview = result['document'][:200].replace('\n', ' ')
                    answer_parts.append(f"{i}. {doc_preview}...")
        
        # Part 4: Generate Enhanced LLM answer
        combined_evidence = []
        for result in sebi_results[:5]:  # Use top 5
            combined_evidence.append(QueryResult(
                document=result['document'],
                metadata=result['metadata'],
                similarity_score=result['score'],
                source='sebi_regulatory'
            ))
        for result in amlsim_results[:3]:  # Use top 3
            combined_evidence.append(QueryResult(
                document=result['document'],
                metadata=result['metadata'],
                similarity_score=result['score'],
                source='amlsim_transaction'
            ))
        
        # Try to get LLM answer with enhanced prompt
        llm_answer = ""
        if self.rag_engine.use_ollama or self.rag_engine.use_claude:
            try:
                llm_answer = await self._generate_enhanced_answer(
                    query, combined_evidence, graph_context, patterns
                )
                answer_parts.append("\n\n**AI ANALYSIS:**")
                answer_parts.append(llm_answer)
            except Exception as e:
                logger.warning(f"LLM generation failed: {e}")
        
        return "\n".join(answer_parts)
    
    async def _generate_enhanced_answer(self, query: str, evidence: List[QueryResult],
                                       graph_context: Dict, patterns: List[Dict]) -> str:
        """
        Generate enhanced answer with document-type awareness and better prompts.
        
        Args:
            query: User query
            evidence: Retrieved evidence
            graph_context: Graph context
            patterns: Cross-domain patterns
            
        Returns:
            Enhanced LLM-generated answer
        """
        # Separate evidence by type
        regulations = []
        cases = []
        transactions = []
        
        for result in evidence:
            doc_type = result.metadata.get('document_type', 'unknown')
            if 'press_release' in doc_type or 'regulation' in doc_type.lower():
                regulations.append(result)
            elif 'adjudication_order' in doc_type:
                cases.append(result)
            elif result.source == 'amlsim_transaction':
                transactions.append(result)
        
        # Build enhanced context
        context_parts = []
        
        # Add regulatory context first (most authoritative)
        if regulations:
            context_parts.append("=== REGULATORY TEXTS ===")
            for i, reg in enumerate(regulations[:3], 1):
                title = reg.metadata.get('title', 'Untitled')[:100]
                context_parts.append(f"\nRegulation {i}: {title}")
                context_parts.append(f"{reg.document[:800]}...")
        
        # Add case precedents
        if cases:
            context_parts.append("\n\n=== CASE PRECEDENTS ===")
            for i, case in enumerate(cases[:3], 1):
                title = case.metadata.get('title', 'Untitled')[:100]
                context_parts.append(f"\nCase {i}: {title}")
                context_parts.append(f"{case.document[:600]}...")
        
        # Add transaction patterns
        if transactions:
            context_parts.append("\n\n=== TRANSACTION PATTERNS ===")
            for i, txn in enumerate(transactions[:2], 1):
                context_parts.append(f"\nPattern {i}:")
                context_parts.append(f"{txn.document[:400]}...")
        
        # Add graph intelligence
        graph_intel = []
        sebi_ctx = graph_context.get('sebi_context', {})
        amlsim_ctx = graph_context.get('amlsim_context', {})
        
        if sebi_ctx.get('available'):
            graph_intel.append(f"- SEBI Database: {sebi_ctx.get('total_entities', 0):,} entities, "
                             f"{sebi_ctx.get('total_violations', 0)} violation types")
        
        if amlsim_ctx.get('available'):
            graph_intel.append(f"- Transaction Network: {amlsim_ctx.get('total_accounts', 0):,} accounts, "
                             f"{amlsim_ctx.get('suspicious_accounts', 0)} flagged as suspicious")
        
        # Build the enhanced prompt
        if self.rag_engine.use_claude:
            prompt = f"""You are an expert financial fraud analyst with deep knowledge of Indian securities regulations (SEBI) and anti-money laundering (AML) frameworks.

TASK: Provide a comprehensive, accurate answer to the user's question using the evidence below.

CONTEXT HIERARCHY (use in this priority order):
1. Regulatory texts (most authoritative - actual laws and rules)
2. Case precedents (enforcement examples and interpretations)  
3. Transaction patterns (real-world fraud indicators)

{chr(10).join(context_parts)}

KNOWLEDGE GRAPH INTELLIGENCE:
{chr(10).join(graph_intel)}

CROSS-DOMAIN PATTERNS:
{f"{len(patterns)} matches found between transactions and regulations" if patterns else "No cross-domain patterns identified"}

USER QUESTION: {query}

INSTRUCTIONS:
1. Answer the question directly and comprehensively
2. PRIORITIZE regulatory texts for rule interpretation
3. Use case precedents to show practical application  
4. Cite specific document types (regulation/case/pattern)
5. Be factual - only state what the evidence supports
6. Structure your answer clearly with sections if needed

Provide your analysis:"""
        else:  # Ollama
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert financial fraud analyst specializing in Indian securities regulations (SEBI) and anti-money laundering (AML). You provide accurate, evidence-based analysis.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Answer this question using the evidence provided. PRIORITIZE regulatory texts over cases.

{chr(10).join(context_parts[:2000])}

Knowledge Graph: {chr(10).join(graph_intel)}

Question: {query}

Provide a clear, factual answer based on the evidence:

<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        # Generate answer
        try:
            if self.rag_engine.use_claude and self.rag_engine.anthropic_client:
                response = await self.rag_engine.anthropic_client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=1200,
                    temperature=0.3,  # Lower temperature for more factual responses
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif self.rag_engine.use_ollama and self.rag_engine.ollama_client:
                response = self.rag_engine.ollama_client.chat(
                    model=self.rag_engine.ollama_model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.3, "num_predict": 800}
                )
                return response['message']['content']
            
        except Exception as e:
            logger.error(f"Enhanced answer generation failed: {e}")
            return "Unable to generate AI analysis. Please refer to the document evidence above."
        
        return "LLM not available for enhanced analysis."
    
    def _build_enhanced_prompt(self, query: str, evidence: List[QueryResult],
                              graph_context: Dict, patterns: List[Dict]) -> str:
        """Build enhanced prompt with graph context."""
        prompt_parts = []
        
        # Add graph statistics
        sebi_ctx = graph_context.get('sebi_context', {})
        amlsim_ctx = graph_context.get('amlsim_context', {})
        
        if sebi_ctx.get('available'):
            prompt_parts.append(f"SEBI Regulatory Context: {sebi_ctx.get('total_violations', 0)} "
                              f"violation types available")
        
        if amlsim_ctx.get('available'):
            prompt_parts.append(f"AMLSim Transaction Context: {amlsim_ctx.get('suspicious_accounts', 0)} "
                              f"suspicious accounts identified")
        
        # Add cross-domain patterns
        if patterns:
            prompt_parts.append(f"Cross-Domain Patterns: {len(patterns)} matches found")
        
        return "\n".join(prompt_parts)
    
    def get_unified_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics from both knowledge graphs.
        
        Returns:
            Combined statistics
        """
        sebi_stats = self.sebi_graph.get_sebi_statistics()
        amlsim_stats = self.amlsim_graph.get_amlsim_statistics()
        
        return {
            'sebi_graph': sebi_stats,
            'amlsim_graph': amlsim_stats,
            'combined': {
                'total_nodes': sebi_stats['total_nodes'] + amlsim_stats['total_nodes'],
                'total_edges': sebi_stats['total_edges'] + amlsim_stats['total_edges'],
                'sebi_entities': sebi_stats['sebi_specific']['entities'],
                'amlsim_accounts': amlsim_stats['amlsim_specific']['accounts'],
                'sebi_violations': sebi_stats['sebi_specific']['violations'],
                'amlsim_fraud_rings': amlsim_stats['pattern_detection'].get('fan_out_patterns', 0)
            }
        }
    
    def _normalize_violation_name(self, name: str) -> str:
        """
        Normalize violation names for consistent matching.
        
        Args:
            name: Violation name with spaces or special chars
            
        Returns:
            Normalized name for graph lookup
        """
        return name.lower().strip().replace(" ", "_").replace("-", "_")
    
    async def trace_transaction_with_regulatory_context(self, account_id: str) -> Dict[str, Any]:
        """
        Trace transaction flow and match with SEBI regulatory cases.
        
        Args:
            account_id: Account to analyze
            
        Returns:
            Transaction trace with regulatory context
        """
        # Trace money flow in AMLSim graph
        money_flow = self.amlsim_graph.trace_money_flow(f"account_{account_id}", max_hops=3)
        
        # Find similar SEBI cases based on pattern
        # Try multiple violation types for better matching
        pattern_type = "money_laundering" if money_flow['net_flow'] < 0 else "fraud"
        
        sebi_cases = []
        # Try normalized versions
        for variation in [pattern_type, pattern_type.replace("_", " "), "fraud"]:
            cases = self.sebi_graph.find_similar_cases(variation, limit=5)
            if cases:
                sebi_cases = cases
                break
        
        return {
            'account': account_id,
            'money_flow': money_flow,
            'pattern_identified': pattern_type,
            'similar_sebi_cases': sebi_cases,
            'regulatory_risk': 'HIGH' if sebi_cases else 'MEDIUM'
        }
    
    def find_accounts_matching_sebi_violations(self, violation_type: str) -> List[Dict]:
        """
        Find AMLSim accounts with patterns matching SEBI violation type.
        
        Args:
            violation_type: SEBI violation type to match
            
        Returns:
            List of matching accounts with patterns
        """
        # Get SEBI cases for this violation - try multiple variations
        sebi_cases = []
        normalized_violation = self._normalize_violation_name(violation_type)
        
        # Try different variations to find matches
        variations = [
            violation_type,  # Original
            normalized_violation,  # Normalized with underscores
            violation_type.replace("_", " "),  # With spaces
            "fraud",  # Fallback to general fraud
            "money_laundering"  # Common AML case
        ]
        
        for variation in variations:
            cases = self.sebi_graph.find_similar_cases(variation, limit=10)
            if cases:
                sebi_cases = cases
                logger.info(f"Found {len(cases)} SEBI cases for '{variation}'")
                break
        
        # Detect patterns in AMLSim that might match
        matching_accounts = []
        
        # For money laundering/fraud violations, look for fan-out/fan-in patterns
        if any(term in violation_type.lower() for term in ['money', 'laundering', 'fraud', 'layering', 'structuring']):
            # Find accounts with fan-out/fan-in patterns
            fraud_rings = self.amlsim_graph.extract_fraud_patterns(max_hops=2)
            
            for ring in fraud_rings[:10]:
                matching_accounts.append({
                    'account': ring['core_account'],
                    'pattern_type': ring['pattern_type'],
                    'amount': ring['total_amount'],
                    'risk_level': ring['risk_level'],
                    'sebi_match': violation_type,
                    'sebi_cases_found': len(sebi_cases),
                    'ring_members': ring['member_count'],
                    'transaction_paths': ring['transaction_paths']
                })
        
        logger.info(f"Found {len(matching_accounts)} accounts matching '{violation_type}' with {len(sebi_cases)} SEBI cases")
        return matching_accounts

