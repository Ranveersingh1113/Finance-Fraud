"""
Text File Processor for FIU and Income Tax documents.
Handles text file reading, cleaning, and basic document structure extraction.
"""
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TextDocument:
    """Data class for processed text documents."""
    document_id: str
    title: str
    document_type: str
    content: str
    file_path: str
    date: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TextFileProcessor:
    """Processor for reading and processing text files (FIU, Income Tax, etc.)."""
    
    def __init__(self):
        """Initialize text file processor."""
        pass
    
    def process_file(self, file_path: Path) -> Optional[TextDocument]:
        """
        Process a single text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            TextDocument object or None if processing fails
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content or len(content.strip()) < 50:
                logger.warning(f"Insufficient content in {file_path}")
                return None
            
            # Extract document metadata from filename
            doc_id = file_path.stem
            title = self._extract_title(file_path, content)
            doc_type = self._detect_document_type(file_path, content)
            
            # Clean content
            cleaned_content = self._clean_content(content)
            
            # Extract date from filename or content
            date = self._extract_date(file_path, content)
            
            # Create metadata
            metadata = {
                'file_name': file_path.name,
                'file_path': str(file_path),
                'word_count': len(cleaned_content.split()),
                'char_count': len(cleaned_content),
                'source': 'fiu' if 'fiu' in str(file_path).lower() else 'incometax'
            }
            
            return TextDocument(
                document_id=doc_id,
                title=title,
                document_type=doc_type,
                content=cleaned_content,
                file_path=str(file_path),
                date=date,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None
    
    def process_all_files(self, directory: Path) -> List[TextDocument]:
        """
        Process all text files in a directory.
        
        Args:
            directory: Directory containing text files
            
        Returns:
            List of TextDocument objects
        """
        documents = []
        
        if not directory.exists():
            logger.warning(f"Directory {directory} does not exist")
            return documents
        
        # Find all .txt files
        txt_files = list(directory.glob("*.txt"))
        logger.info(f"Found {len(txt_files)} text files in {directory}")
        
        for txt_file in txt_files:
            doc = self.process_file(txt_file)
            if doc:
                documents.append(doc)
        
        logger.info(f"Processed {len(documents)} documents from {directory}")
        return documents
    
    def _extract_title(self, file_path: Path, content: str) -> str:
        """Extract title from filename or content."""
        # Try to get title from filename (remove extension, clean up)
        title = file_path.stem
        title = title.replace('_', ' ').replace('-', ' ')
        title = re.sub(r'(\d+)', r' \1', title)  # Add space before numbers
        title = ' '.join(title.split())  # Normalize whitespace
        
        # If filename is too generic, try first line of content
        if len(title) < 10:
            first_line = content.split('\n')[0].strip()
            if len(first_line) > 10 and len(first_line) < 200:
                title = first_line
        
        return title
    
    def _detect_document_type(self, file_path: Path, content: str) -> str:
        """Detect document type from filename and content."""
        filename_lower = file_path.name.lower()
        content_lower = content.lower()[:1000]  # Check first 1000 chars
        
        # FIU document types
        if 'fiu' in str(file_path.parent).lower():
            if 'order' in filename_lower:
                return 'fiu_order'
            elif 'pmla' in filename_lower or 'pmla' in content_lower:
                return 'pmla_act'
            elif any(word in filename_lower for word in ['furnishing', 'identity', 'maintenance', 'reporting']):
                return 'fiu_guideline'
            else:
                return 'fiu_document'
        
        # Income Tax document types
        elif 'incometax' in str(file_path.parent).lower():
            if 'charter' in filename_lower:
                return 'taxpayer_charter'
            elif 'circular' in filename_lower or 'notification' in filename_lower:
                return 'tax_circular'
            elif 'directory' in filename_lower:
                return 'tax_directory'
            elif 'grievance' in filename_lower:
                return 'grievance_redressal'
            else:
                return 'tax_document'
        
        return 'document'
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize text content."""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove non-printable characters (keep common unicode)
        content = re.sub(r'[^\x20-\x7E\u00A0-\uFFFF]', ' ', content)
        
        # Normalize line breaks
        content = re.sub(r'\r\n', '\n', content)
        content = re.sub(r'\r', '\n', content)
        
        # Remove excessive newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
    
    def _extract_date(self, file_path: Path, content: str) -> Optional[datetime]:
        """Extract date from filename or content."""
        # Try to extract date from filename (common patterns: YYYY, YYYY_MM, etc.)
        filename = file_path.stem
        
        # Pattern: YYYY
        year_match = re.search(r'\b(19|20)\d{2}\b', filename)
        if year_match:
            year = int(year_match.group())
            # Default to January 1st if only year found
            try:
                return datetime(year, 1, 1)
            except:
                pass
        
        # Pattern: YYYY_MM or YYYY-MM
        date_match = re.search(r'\b(19|20)\d{2}[_-](\d{1,2})\b', filename)
        if date_match:
            year = int(date_match.group(1))
            month = int(date_match.group(2))
            try:
                return datetime(year, month, 1)
            except:
                pass
        
        # Try to extract from content (first few lines)
        content_lines = content.split('\n')[:20]
        for line in content_lines:
            # Look for date patterns like "YYYY-MM-DD", "DD/MM/YYYY", etc.
            date_patterns = [
                r'\b(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})\b',
                r'\b(\d{1,2})[-\/](\d{1,2})[-\/](\d{4})\b',
            ]
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        if len(match.group(1)) == 4:  # YYYY-MM-DD
                            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                        else:  # DD/MM/YYYY
                            day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                        return datetime(year, month, day)
                    except:
                        continue
        
        return None

