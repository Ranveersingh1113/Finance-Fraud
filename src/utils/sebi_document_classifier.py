"""
SEBI Document Classifier
Intelligently categorize SEBI documents into relevant types for fraud analysis.
"""

from typing import Dict, List
import re


class SEBIDocumentClassifier:
    """
    Classify SEBI documents into categories for intelligent filtering.
    
    This replaces brittle keyword-based filtering with a maintainable,
    extensible classification system.
    """
    
    # Document categories with their identifying keywords
    CATEGORIES = {
        'AML': [
            'money laundering', 'aml', 'anti-money laundering',
            'suspicious transaction', 'pmla', 'prevention of money laundering',
            'combating financing of terrorism', 'cft', 'financial intelligence unit',
            'fiu', 'know your customer', 'kyc'
        ],
        'FRAUD': [
            'fraudulent', 'unfair trade', 'market manipulation', 'fraud',
            'prohibition of fraudulent', 'insider trading', 'front running',
            'price manipulation', 'circular trading', 'wash trade'
        ],
        'INSIDER_TRADING': [
            'insider trading', 'upsi', 'unpublished price sensitive',
            'pit regulations', 'prohibition of insider trading'
        ],
        'MARKET_ABUSE': [
            'market abuse', 'market misconduct', 'unfair trade practices',
            'manipulative trading', 'spoofing', 'layering'
        ],
        'COMPLIANCE': [
            'compliance', 'regulatory compliance', 'intermediary obligations',
            'reporting requirements', 'disclosure requirements'
        ],
        'IRRELEVANT': [
            'employee benefit', 'sweat equity', 'listing obligation', 'lodr',
            'depositor', 'share based', 'disclosure requirement',
            'corporate governance', 'buyback', 'dividend',
            'annual general meeting', 'agm', 'board meeting'
        ]
    }
    
    # Query type to relevant categories mapping
    QUERY_RELEVANCE = {
        'account_trace': ['AML', 'FRAUD', 'MARKET_ABUSE', 'COMPLIANCE'],
        'regulatory_query': ['AML', 'FRAUD', 'INSIDER_TRADING', 'MARKET_ABUSE', 'COMPLIANCE'],
        'pattern_analysis': ['AML', 'FRAUD', 'MARKET_ABUSE'],
        'enforcement': ['AML', 'FRAUD', 'INSIDER_TRADING', 'MARKET_ABUSE']
    }
    
    def __init__(self):
        """Initialize the classifier."""
        # Pre-compile regex patterns for performance
        self._compiled_patterns = {}
        for category, keywords in self.CATEGORIES.items():
            # Create a single regex pattern for each category
            pattern = '|'.join(re.escape(kw) for kw in keywords)
            self._compiled_patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def classify(self, document: str, max_length: int = 2000) -> str:
        """
        Classify a document into a category.
        
        Args:
            document: Document text to classify
            max_length: Maximum document length to analyze (for performance)
            
        Returns:
            Category name (e.g., 'AML', 'FRAUD', 'IRRELEVANT')
        """
        # Only analyze first portion of document for performance
        doc_sample = document[:max_length].lower()
        
        # Score each category
        scores: Dict[str, int] = {}
        for category, pattern in self._compiled_patterns.items():
            matches = pattern.findall(doc_sample)
            scores[category] = len(matches)
        
        # If no matches, return unknown
        if sum(scores.values()) == 0:
            return 'UNKNOWN'
        
        # Return category with highest score
        return max(scores, key=scores.get)
    
    def classify_with_confidence(self, document: str, max_length: int = 2000) -> tuple[str, float]:
        """
        Classify document and return confidence score.
        
        Args:
            document: Document text
            max_length: Maximum length to analyze
            
        Returns:
            Tuple of (category, confidence_score)
        """
        doc_sample = document[:max_length].lower()
        
        scores: Dict[str, int] = {}
        for category, pattern in self._compiled_patterns.items():
            matches = pattern.findall(doc_sample)
            scores[category] = len(matches)
        
        total_matches = sum(scores.values())
        if total_matches == 0:
            return 'UNKNOWN', 0.0
        
        top_category = max(scores, key=scores.get)
        confidence = scores[top_category] / total_matches
        
        return top_category, confidence
    
    def is_relevant_for_query(self, document: str, query_type: str = 'account_trace') -> bool:
        """
        Check if document is relevant for a specific query type.
        
        Args:
            document: Document text
            query_type: Type of query ('account_trace', 'regulatory_query', etc.)
            
        Returns:
            True if document is relevant, False otherwise
        """
        category = self.classify(document)
        
        # Always filter out irrelevant documents
        if category == 'IRRELEVANT':
            return False
        
        # Unknown documents are kept (benefit of doubt)
        if category == 'UNKNOWN':
            return True
        
        # Check if category is relevant for this query type
        relevant_categories = self.QUERY_RELEVANCE.get(query_type, [])
        return category in relevant_categories
    
    def get_category_keywords(self, category: str) -> List[str]:
        """
        Get keywords for a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of keywords for that category
        """
        return self.CATEGORIES.get(category, [])
    
    def filter_relevant_documents(
        self, 
        documents: List[Dict], 
        query_type: str = 'account_trace',
        document_key: str = 'document'
    ) -> List[Dict]:
        """
        Filter a list of document results to keep only relevant ones.
        
        Args:
            documents: List of document dicts with text content
            query_type: Type of query being performed
            document_key: Key in dict containing document text
            
        Returns:
            Filtered list of relevant documents
        """
        filtered = []
        for doc in documents:
            doc_text = doc.get(document_key, '')
            if self.is_relevant_for_query(doc_text, query_type):
                # Add classification metadata
                category, confidence = self.classify_with_confidence(doc_text)
                doc['classification'] = {
                    'category': category,
                    'confidence': confidence
                }
                filtered.append(doc)
        
        return filtered
    
    def prioritize_documents(
        self,
        documents: List[Dict],
        query_type: str = 'account_trace',
        document_key: str = 'document'
    ) -> List[Dict]:
        """
        Sort documents by relevance priority.
        
        Prioritizes AML/FRAUD documents for account traces,
        maintains original scoring but boosts relevant categories.
        
        Args:
            documents: List of document dicts
            query_type: Query type
            document_key: Key containing document text
            
        Returns:
            Sorted list with most relevant documents first
        """
        def priority_score(doc: Dict) -> tuple:
            """Calculate priority score for sorting."""
            doc_text = doc.get(document_key, '')
            category, confidence = self.classify_with_confidence(doc_text)
            
            # Base score from similarity/relevance
            base_score = doc.get('score', 0)
            
            # Category boost
            category_boost = 0
            relevant_categories = self.QUERY_RELEVANCE.get(query_type, [])
            if category in relevant_categories:
                # AML and FRAUD get highest boost for account traces
                if category in ['AML', 'FRAUD'] and query_type in ['account_trace', 'pattern_analysis']:
                    category_boost = 0.3
                else:
                    category_boost = 0.15
            elif category == 'IRRELEVANT':
                category_boost = -0.5  # Demote irrelevant
            
            # Confidence boost
            confidence_boost = confidence * 0.1
            
            final_score = base_score + category_boost + confidence_boost
            
            # Return tuple for sorting: (is_relevant, final_score)
            # This ensures relevant docs always come first
            is_relevant = category in relevant_categories
            return (is_relevant, final_score)
        
        return sorted(documents, key=priority_score, reverse=True)

