"""
SEBI File Processor for manually downloaded SEBI documents.
Handles PDF and text file processing for Indian financial fraud data.
"""
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import pandas as pd
import PyPDF2
import pdfplumber
import fitz  # pymupdf
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SEBIDocument:
    """Data class for SEBI documents."""
    document_id: str
    title: str
    document_type: str
    file_path: str
    date: Optional[datetime]
    content: str
    metadata: Dict[str, Any]


class SEBIFileProcessor:
    """Processor for manually downloaded SEBI documents."""
    
    def __init__(self, sebi_directory: str = "./data/sebi"):
        """
        Initialize SEBI file processor.
        
        Args:
            sebi_directory: Directory containing manually downloaded SEBI files
        """
        self.sebi_directory = Path(sebi_directory)
        self.sebi_directory.mkdir(parents=True, exist_ok=True)
        
        # Supported file extensions
        self.supported_extensions = {'.pdf', '.txt', '.doc', '.docx'}
        
        # Document type mapping based on file patterns
        self.document_type_patterns = {
            'adjudication_order': [
                r'adjudication.*order',
                r'ao.*\d{4}',
                r'order.*\d{4}',
                r'adjudicating.*officer'
            ],
            'investigation_report': [
                r'investigation.*report',
                r'inquiry.*report',
                r'committee.*report',
                r'fact.*finding'
            ],
            'press_release': [
                r'press.*release',
                r'media.*release',
                r'circular',
                r'advisory'
            ]
        }
    
    def scan_sebi_files(self) -> List[Path]:
        """
        Scan the SEBI directory for supported files.
        
        Returns:
            List of file paths to process
        """
        logger.info(f"Scanning SEBI directory: {self.sebi_directory}")
        
        files = []
        for ext in self.supported_extensions:
            pattern = f"**/*{ext}"
            files.extend(self.sebi_directory.glob(pattern))
        
        # Also look for files without extensions that might be text
        for file_path in self.sebi_directory.rglob("*"):
            if file_path.is_file() and not file_path.suffix:
                # Check if it might be a text file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read(100)  # Read first 100 chars
                    files.append(file_path)
                except:
                    pass
        
        logger.info(f"Found {len(files)} SEBI files to process")
        return files
    
    def process_file(self, file_path: Path) -> Optional[SEBIDocument]:
        """
        Process a single SEBI file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            SEBIDocument object or None if processing failed
        """
        try:
            logger.info(f"Processing file: {file_path.name}")
            
            # Extract content based on file type
            content = self._extract_file_content(file_path)
            if not content:
                logger.warning(f"No content extracted from {file_path.name}")
                return None
            
            # Determine document type
            doc_type = self._determine_document_type(file_path.name, content)
            
            # Extract metadata
            metadata = self._extract_document_metadata(content)
            
            # Parse date from filename or content
            date = self._extract_date_from_filename(file_path.name, content)
            
            # Generate document ID using filename and timestamp
            import time
            timestamp = int(time.time() * 1000)  # milliseconds
            filename_hash = hash(str(file_path)) % 10000
            doc_id = f"SEBI_{doc_type.upper()}_{timestamp}_{filename_hash}"
            
            # Create title from filename or content
            title = self._generate_document_title(file_path.name, content)
            
            document = SEBIDocument(
                document_id=doc_id,
                title=title,
                document_type=doc_type,
                file_path=str(file_path),
                date=date,
                content=content,
                metadata=metadata
            )
            
            logger.info(f"Successfully processed: {title}")
            return document
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None
    
    def _extract_file_content(self, file_path: Path) -> str:
        """Extract content from various file types."""
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.pdf':
                return self._extract_pdf_content(file_path)
            elif extension in ['.txt']:
                return self._extract_text_content(file_path)
            elif extension in ['.doc', '.docx']:
                return self._extract_word_content(file_path)
            else:
                # Try as text file
                return self._extract_text_content(file_path)
        except Exception as e:
            logger.error(f"Error extracting content from {file_path}: {e}")
            return ""
    
    def _extract_pdf_content(self, file_path: Path) -> str:
        """Extract text from PDF using multiple methods."""
        content = ""
        
        # Method 1: PyPDF2
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed for {file_path}: {e}")
        
        # Method 2: pdfplumber (if PyPDF2 failed or content is short)
        if len(content) < 100:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            content += text + "\n"
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed for {file_path}: {e}")
        
        # Method 3: pymupdf (if other methods failed)
        if len(content) < 100:
            try:
                pdf_document = fitz.open(file_path)
                for page_num in range(pdf_document.page_count):
                    page = pdf_document[page_num]
                    content += page.get_text() + "\n"
                pdf_document.close()
            except Exception as e:
                logger.warning(f"pymupdf extraction failed for {file_path}: {e}")
        
        return self._clean_extracted_text(content)
    
    def _extract_text_content(self, file_path: Path) -> str:
        """Extract content from text files."""
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return self._clean_extracted_text(content)
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"Error reading {file_path} with {encoding}: {e}")
        
        logger.error(f"Could not read {file_path} with any encoding")
        return ""
    
    def _extract_word_content(self, file_path: Path) -> str:
        """Extract content from Word documents."""
        try:
            # Try to read as text if it's actually a text file with .doc extension
            return self._extract_text_content(file_path)
        except:
            logger.warning(f"Word document processing not implemented for {file_path}")
            return ""
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean extracted text by removing common artifacts."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize line breaks
        
        # Remove common headers/footers
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip very short lines that are likely artifacts
            if len(line) < 3:
                continue
            # Skip lines that are mostly numbers (likely page numbers)
            if re.match(r'^\d+$', line):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _determine_document_type(self, filename: str, content: str) -> str:
        """Determine document type based on filename and content."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Check each document type pattern
        for doc_type, patterns in self.document_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, filename_lower) or re.search(pattern, content_lower):
                    return doc_type
        
        # Default to adjudication order if no pattern matches
        return 'adjudication_order'
    
    def _extract_document_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from document content."""
        metadata = {}
        
        # Extract violation types
        violation_types = self._extract_violation_types(content)
        metadata['violation_types'] = violation_types
        
        # Extract entities
        entities = self._extract_entities(content)
        metadata['entities'] = entities
        
        # Extract penalty information
        penalty_info = self._extract_penalty_information(content)
        metadata['penalty_info'] = penalty_info
        
        # Extract key financial terms
        financial_terms = self._extract_financial_terms(content)
        metadata['financial_terms'] = financial_terms
        
        # Calculate content statistics
        metadata['word_count'] = len(content.split())
        metadata['sentence_count'] = len(re.split(r'[.!?]+', content))
        
        return metadata
    
    def _extract_violation_types(self, content: str) -> List[str]:
        """Extract violation types from content."""
        fraud_patterns = {
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
        
        violation_types = []
        content_lower = content.lower()
        
        for violation_type, patterns in fraud_patterns.items():
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    violation_types.append(violation_type)
                    break
        
        return list(set(violation_types))
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract entities from content."""
        entity_patterns = {
            'companies': r'\b[A-Z][a-zA-Z\s&\.]+(?:Ltd|Limited|Corp|Corporation|Inc|Incorporated|Private|Public)\b',
            'individuals': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',
            'penalties': r'₹[\d,]+(?:\.\d{2})?(?:\s*(?:lakh|crore|million|billion))?',
            'dates': r'\b\d{1,2}[-\/]\d{1,2}[-\/]\d{4}\b|\b\d{4}[-\/]\d{1,2}[-\/]\d{1,2}\b',
            'case_numbers': r'\b[A-Z]+[/-]\d{2}[/-]\d{4}\b|\b\d{4}[/-][A-Z]+[/-]\d+\b'
        }
        
        entities = {}
        for entity_type, pattern in entity_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                entities[entity_type] = list(set(matches))
        
        return entities
    
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
    
    def _extract_date_from_filename(self, filename: str, content: str) -> Optional[datetime]:
        """Extract date from filename or content."""
        # Try to extract date from filename first
        date_patterns = [
            r'(\d{4})[-_](\d{1,2})[-_](\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})[-_](\d{1,2})[-_](\d{4})',  # DD-MM-YYYY or MM-DD-YYYY
            r'(\d{4})',  # Just year
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 3:
                        # Try different date formats
                        for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y']:
                            try:
                                return datetime.strptime('-'.join(groups), fmt)
                            except ValueError:
                                continue
                    elif len(groups) == 1:
                        # Just year
                        return datetime(int(groups[0]), 1, 1)
                except:
                    continue
        
        # Try to extract from content
        return self._extract_date_from_content(content)
    
    def _extract_date_from_content(self, content: str) -> Optional[datetime]:
        """Extract date from document content."""
        date_patterns = [
            r'(\d{1,2}[-\/]\d{1,2}[-\/]\d{4})',
            r'(\d{4}[-\/]\d{1,2}[-\/]\d{1,2})',
            r'([A-Za-z]+ \d{1,2}, \d{4})',
            r'(\d{1,2} [A-Za-z]+ \d{4})',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            if matches:
                try:
                    date_str = matches[0]
                    # Try different date formats
                    for fmt in ['%d-%m-%Y', '%Y-%m-%d', '%B %d, %Y', '%d %B %Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except:
                    continue
        
        return None
    
    def _generate_document_title(self, filename: str, content: str) -> str:
        """Generate a document title from filename or content."""
        # Clean filename
        title = filename.replace('_', ' ').replace('-', ' ')
        title = re.sub(r'\.(pdf|txt|doc|docx)$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # If title is too generic, try to extract from content
        if len(title) < 20 or title.lower() in ['order', 'report', 'document']:
            # Look for common title patterns in content
            title_patterns = [
                r'IN THE MATTER OF (.+?)(?:\.|$)',
                r'ORDER NO\. (.+?)(?:\.|$)',
                r'REPORT ON (.+?)(?:\.|$)',
                r'INVESTIGATION OF (.+?)(?:\.|$)',
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    extracted_title = match.group(1).strip()
                    if len(extracted_title) > 10:
                        return extracted_title[:100]  # Limit length
        
        return title[:100]  # Limit length
    
    def process_all_files(self) -> List[SEBIDocument]:
        """
        Process all SEBI files in the directory.
        
        Returns:
            List of processed SEBI documents
        """
        logger.info("Starting to process all SEBI files...")
        
        files = self.scan_sebi_files()
        documents = []
        
        for file_path in files:
            document = self.process_file(file_path)
            if document:
                documents.append(document)
        
        logger.info(f"Successfully processed {len(documents)} documents")
        return documents
    
    def save_documents_to_csv(self, documents: List[SEBIDocument], filename: str = "sebi_documents.csv") -> None:
        """Save processed documents to CSV file."""
        if not documents:
            logger.warning("No documents to save")
            return
        
        data = []
        for doc in documents:
            data.append({
                'document_id': doc.document_id,
                'title': doc.title,
                'document_type': doc.document_type,
                'file_path': doc.file_path,
                'date': doc.date.isoformat() if doc.date else None,
                'content': doc.content[:1000] + "..." if len(doc.content) > 1000 else doc.content,
                'metadata': str(doc.metadata),
                'content_length': len(doc.content)
            })
        
        df = pd.DataFrame(data)
        output_path = self.sebi_directory / filename
        df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Saved {len(documents)} documents to {output_path}")
    
    def get_processing_summary(self, documents: List[SEBIDocument]) -> Dict[str, Any]:
        """Get a summary of processed documents."""
        if not documents:
            return {}
        
        summary = {
            'total_documents': len(documents),
            'document_types': {},
            'violation_types': {},
            'date_range': {},
            'content_statistics': {
                'total_words': 0,
                'average_words_per_doc': 0,
                'total_characters': 0
            }
        }
        
        dates = []
        total_words = 0
        
        for doc in documents:
            # Document type distribution
            doc_type = doc.document_type
            summary['document_types'][doc_type] = summary['document_types'].get(doc_type, 0) + 1
            
            # Violation type distribution
            for violation in doc.metadata.get('violation_types', []):
                summary['violation_types'][violation] = summary['violation_types'].get(violation, 0) + 1
            
            # Date range
            if doc.date:
                dates.append(doc.date)
            
            # Content statistics
            word_count = doc.metadata.get('word_count', 0)
            total_words += word_count
        
        # Date range
        if dates:
            summary['date_range'] = {
                'earliest': min(dates).isoformat(),
                'latest': max(dates).isoformat()
            }
        
        # Content statistics
        summary['content_statistics']['total_words'] = total_words
        summary['content_statistics']['average_words_per_doc'] = total_words / len(documents)
        summary['content_statistics']['total_characters'] = sum(len(doc.content) for doc in documents)
        
        return summary

