"""
SEBI Document Processor for cleaning, chunking, and preparing documents for RAG.
Handles text preprocessing, semantic chunking, and metadata extraction.
"""
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

logger = logging.getLogger(__name__)


@dataclass
class ProcessedChunk:
    """Data class for processed document chunks."""
    chunk_id: str
    document_id: str
    document_type: str
    title: str
    content: str
    chunk_index: int
    metadata: Dict[str, Any]
    keywords: List[str]
    entities: List[str]
    violation_types: List[str]
    url: Optional[str] = None
    date: Optional[datetime] = None


class SEBIProcessor:
    """Processor for cleaning and chunking SEBI documents."""
    
    def __init__(self, min_chunk_size: int = 200, max_chunk_size: int = 1000):
        """
        Initialize SEBI processor.
        
        Args:
            min_chunk_size: Minimum size for document chunks
            max_chunk_size: Maximum size for document chunks
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        
        # Initialize text processing tools
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Add Indian financial terms to stop words
        self.stop_words.update([
            'sebi', 'securities', 'exchange', 'board', 'india', 'order', 'act',
            'regulations', 'rules', 'scheme', 'company', 'companies', 'corporation',
            'limited', 'ltd', 'private', 'public', 'plc', 'inc', 'corp'
        ])
        
        # Financial fraud patterns
        self.fraud_patterns = {
            'insider_trading': [
                'insider trading', 'insider information', 'unpublished price sensitive information',
                'upsi', 'material non-public information', 'mnpi'
            ],
            'market_manipulation': [
                'market manipulation', 'price manipulation', 'price rigging', 'circular trading',
                'wash trading', 'matched orders', 'artificial price', 'false market'
            ],
            'disclosure_violations': [
                'disclosure violation', 'non-disclosure', 'material disclosure', 'timely disclosure',
                'periodic disclosure', 'event disclosure', 'continuous disclosure'
            ],
            'accounting_fraud': [
                'accounting fraud', 'financial misstatement', 'cooking books', 'window dressing',
                'revenue recognition', 'asset misstatement', 'liability misstatement'
            ],
            'money_laundering': [
                'money laundering', 'layering', 'integration', 'placement', 'suspicious transaction',
                'benami transaction', 'shell company', 'round tripping'
            ],
            'corporate_governance': [
                'corporate governance', 'board composition', 'independent directors', 'related party',
                'conflict of interest', 'fiduciary duty', 'audit committee'
            ]
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            'companies': r'\b[A-Z][a-zA-Z\s&\.]+(?:Ltd|Limited|Corp|Corporation|Inc|Incorporated|Private|Public)\b',
            'individuals': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',
            'penalties': r'₹[\d,]+(?:\.\d{2})?(?:\s*(?:lakh|crore|million|billion))?',
            'dates': r'\b\d{1,2}[-\/]\d{1,2}[-\/]\d{4}\b|\b\d{4}[-\/]\d{1,2}[-\/]\d{1,2}\b',
            'case_numbers': r'\b[A-Z]+[/-]\d{2}[/-]\d{4}\b|\b\d{4}[/-][A-Z]+[/-]\d+\b'
        }
    
    def process_documents(self, documents: List[Dict[str, Any]]) -> List[ProcessedChunk]:
        """
        Process a list of SEBI documents into chunks.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of processed chunks
        """
        logger.info(f"Processing {len(documents)} SEBI documents...")
        
        all_chunks = []
        
        for doc in documents:
            try:
                chunks = self.process_single_document(doc)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.warning(f"Error processing document {doc.get('document_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Generated {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
    
    def process_single_document(self, document: Dict[str, Any]) -> List[ProcessedChunk]:
        """
        Process a single SEBI document into chunks.
        
        Args:
            document: Document dictionary
            
        Returns:
            List of processed chunks
        """
        doc_id = document.get('document_id', 'unknown')
        content = document.get('content', '')
        
        if not content:
            logger.warning(f"No content found for document {doc_id}")
            return []
        
        # Clean and preprocess content
        cleaned_content = self._clean_document_content(content)
        
        # Extract metadata
        metadata = self._extract_document_metadata(document, cleaned_content)
        
        # Split into semantic chunks
        chunks = self._create_semantic_chunks(cleaned_content, doc_id, document, metadata)
        
        return chunks
    
    def _clean_document_content(self, content: str) -> str:
        """Clean document content by removing artifacts and normalizing text."""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common PDF artifacts
        content = re.sub(r'[^\x00-\x7F]+', ' ', content)  # Remove non-ASCII
        content = re.sub(r'\f', '\n', content)  # Replace form feeds with newlines
        
        # Remove page numbers and headers/footers
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines that are just numbers (page numbers)
            if re.match(r'^\d+$', line):
                continue
            
            # Skip very short lines that are likely headers/footers
            if len(line) < 5:
                continue
            
            # Skip lines that are mostly punctuation
            if len(re.sub(r'[^\w\s]', '', line)) < len(line) * 0.3:
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_document_metadata(self, document: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Extract metadata from document and content."""
        metadata = document.get('metadata', {})
        if isinstance(metadata, str):
            metadata = eval(metadata) if metadata else {}
        
        # Extract violation types from content
        violation_types = self._extract_violation_types(content)
        metadata['violation_types'] = violation_types
        
        # Extract entities
        entities = self._extract_entities(content)
        metadata['entities'] = entities
        
        # Extract key financial terms
        financial_terms = self._extract_financial_terms(content)
        metadata['financial_terms'] = financial_terms
        
        # Extract penalty information
        penalty_info = self._extract_penalty_information(content)
        metadata['penalty_info'] = penalty_info
        
        # Calculate content statistics
        metadata['word_count'] = len(content.split())
        metadata['sentence_count'] = len(sent_tokenize(content))
        metadata['paragraph_count'] = len([p for p in content.split('\n\n') if p.strip()])
        
        return metadata
    
    def _extract_violation_types(self, content: str) -> List[str]:
        """Extract violation types from content."""
        violation_types = []
        content_lower = content.lower()
        
        for violation_type, patterns in self.fraud_patterns.items():
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    violation_types.append(violation_type)
                    break
        
        return list(set(violation_types))
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract entities from content."""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                entities[entity_type] = list(set(matches))
        
        return entities
    
    def _extract_financial_terms(self, content: str) -> List[str]:
        """Extract financial terms from content."""
        financial_terms = [
            'revenue', 'profit', 'loss', 'assets', 'liabilities', 'equity', 'debt',
            'market cap', 'market capitalization', 'eps', 'pe ratio', 'dividend',
            'ipo', 'fpo', 'merger', 'acquisition', 'takeover', 'delisting',
            'mutual fund', 'portfolio', 'investment', 'securities', 'bonds',
            'derivatives', 'futures', 'options', 'commodities', 'forex'
        ]
        
        found_terms = []
        content_lower = content.lower()
        
        for term in financial_terms:
            if term.lower() in content_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _extract_penalty_information(self, content: str) -> Dict[str, Any]:
        """Extract penalty information from content."""
        penalty_info = {}
        
        # Extract penalty amounts
        penalty_patterns = [
            r'penalty[:\s]+(?:of\s+)?₹([\d,]+(?:\.\d{2})?)',
            r'fine[:\s]+(?:of\s+)?₹([\d,]+(?:\.\d{2})?)',
            r'₹([\d,]+(?:\.\d{2})?)\s*(?:lakh|crore|million|billion)',
        ]
        
        penalties = []
        for pattern in penalty_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            penalties.extend(matches)
        
        if penalties:
            penalty_info['amounts'] = penalties
        
        # Extract penalty types
        penalty_types = [
            'monetary penalty', 'disgorgement', 'cease and desist', 'prohibition',
            'suspension', 'cancellation', 'warning', 'admonition'
        ]
        
        found_types = []
        content_lower = content.lower()
        
        for penalty_type in penalty_types:
            if penalty_type in content_lower:
                found_types.append(penalty_type)
        
        if found_types:
            penalty_info['types'] = found_types
        
        return penalty_info
    
    def _create_semantic_chunks(self, content: str, doc_id: str, document: Dict[str, Any], metadata: Dict[str, Any]) -> List[ProcessedChunk]:
        """Create semantic chunks from document content."""
        chunks = []
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        current_chunk = ""
        chunk_index = 0
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed max size, create a chunk
            if len(current_chunk) + len(paragraph) > self.max_chunk_size and current_chunk:
                if len(current_chunk) >= self.min_chunk_size:
                    chunk = self._create_chunk(
                        current_chunk, doc_id, document, metadata, chunk_index
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Add the last chunk
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunk = self._create_chunk(
                current_chunk, doc_id, document, metadata, chunk_index
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, content: str, doc_id: str, document: Dict[str, Any], metadata: Dict[str, Any], chunk_index: int) -> ProcessedChunk:
        """Create a processed chunk from content."""
        # Extract keywords from chunk content
        keywords = self._extract_keywords(content)
        
        # Extract entities specific to this chunk
        chunk_entities = self._extract_entities(content)
        
        # Extract violation types specific to this chunk
        chunk_violation_types = self._extract_violation_types(content)
        
        # Create chunk metadata
        chunk_metadata = {
            'document_title': document.get('title', ''),
            'document_type': document.get('document_type', ''),
            'document_date': document.get('date', ''),
            'document_url': document.get('url', ''),
            'chunk_length': len(content),
            'chunk_word_count': len(content.split()),
            'violation_types': chunk_violation_types,
            'entities': chunk_entities,
            'financial_terms': self._extract_financial_terms(content),
            'penalty_info': self._extract_penalty_information(content)
        }
        
        return ProcessedChunk(
            chunk_id=f"{doc_id}_chunk_{chunk_index}",
            document_id=doc_id,
            document_type=document.get('document_type', 'unknown'),
            title=document.get('title', ''),
            content=content,
            chunk_index=chunk_index,
            metadata=chunk_metadata,
            keywords=keywords,
            entities=list(chunk_entities.keys()),
            violation_types=chunk_violation_types,
            url=document.get('url') or document.get('file_path'),
            date=document.get('date')
        )
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content using TF-IDF."""
        try:
            # Tokenize and clean text
            words = word_tokenize(content.lower())
            words = [self.lemmatizer.lemmatize(word) for word in words]
            words = [word for word in words if word.isalpha() and word not in self.stop_words]
            
            if not words:
                return []
            
            # Use TF-IDF to extract important terms
            vectorizer = TfidfVectorizer(max_features=10, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([' '.join(words)])
            
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_indices = np.argsort(tfidf_scores)[-5:]  # Top 5 keywords
            keywords = [feature_names[i] for i in keyword_indices if tfidf_scores[i] > 0]
            
            return keywords
            
        except Exception as e:
            logger.warning(f"Error extracting keywords: {e}")
            return []
    
    def save_processed_chunks(self, chunks: List[ProcessedChunk], output_path: str) -> None:
        """Save processed chunks to CSV file."""
        if not chunks:
            logger.warning("No chunks to save")
            return
        
        data = []
        for chunk in chunks:
            data.append({
                'chunk_id': chunk.chunk_id,
                'document_id': chunk.document_id,
                'document_type': chunk.document_type,
                'title': chunk.title,
                'content': chunk.content,
                'chunk_index': chunk.chunk_index,
                'keywords': ', '.join(chunk.keywords),
                'entities': ', '.join(chunk.entities),
                'violation_types': ', '.join(chunk.violation_types),
                'metadata': str(chunk.metadata),
                'content_length': len(chunk.content),
                'word_count': chunk.metadata.get('chunk_word_count', 0)
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Saved {len(chunks)} processed chunks to {output_path}")
    
    def create_document_summary(self, chunks: List[ProcessedChunk]) -> Dict[str, Any]:
        """Create a summary of processed documents."""
        if not chunks:
            return {}
        
        # Aggregate statistics
        total_chunks = len(chunks)
        total_documents = len(set(chunk.document_id for chunk in chunks))
        
        # Document type distribution
        doc_types = {}
        for chunk in chunks:
            doc_type = chunk.document_type
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        # Violation type distribution
        violation_types = {}
        for chunk in chunks:
            for violation_type in chunk.violation_types:
                violation_types[violation_type] = violation_types.get(violation_type, 0) + 1
        
        # Entity distribution
        all_entities = []
        for chunk in chunks:
            all_entities.extend(chunk.entities)
        
        entity_counts = {}
        for entity in all_entities:
            entity_counts[entity] = entity_counts.get(entity, 0) + 1
        
        # Top entities
        top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Content statistics
        total_words = sum(chunk.metadata.get('chunk_word_count', 0) for chunk in chunks)
        avg_chunk_size = total_words / total_chunks if total_chunks > 0 else 0
        
        summary = {
            'total_chunks': total_chunks,
            'total_documents': total_documents,
            'document_types': doc_types,
            'violation_types': violation_types,
            'top_entities': top_entities,
            'content_statistics': {
                'total_words': total_words,
                'average_chunk_size': avg_chunk_size,
                'chunks_per_document': total_chunks / total_documents if total_documents > 0 else 0
            }
        }
        
        return summary

