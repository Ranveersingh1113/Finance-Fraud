"""
Document Title Extractor
Clean, maintainable title extraction for SEBI documents.
"""

from typing import Optional, Callable, List, Tuple
import re


class DocumentTitleExtractor:
    """
    Extract titles from SEBI documents using pattern matching.
    
    Replaces 50+ lines of nested if/else with a clean pattern-based approach.
    """
    
    def __init__(self):
        """Initialize the extractor with predefined patterns."""
        # Pattern format: (regex_pattern, formatter_function, priority)
        # Higher priority patterns are checked first
        self.patterns: List[Tuple[str, Callable, int]] = [
            # Pattern 1: Subject line (most reliable for Master Circulars)
            (
                r'SUBJECT\s*:\s*(.+?)(?:\n|$)',
                lambda m, doc: self._format_subject_title(m.group(1), doc),
                10  # Highest priority
            ),
            
            # Pattern 2: Master Circular with reference number
            (
                r'MASTER\s+CIRCULAR.*?SEBI/HO/([\w/\-]+)',
                lambda m, doc: f"SEBI Master Circular ({m.group(1)[:30]})",
                9
            ),
            
            # Pattern 3: Adjudication Order with matter
            (
                r'ADJUDICATION\s+ORDER.*?(?:IN\s+THE\s+)?MATTER\s+OF\s+(.{10,100})',
                lambda m, doc: f"SEBI Adjudication Order: {m.group(1).strip()[:80]}",
                9
            ),
            
            # Pattern 4: Generic Adjudication Order
            (
                r'ADJUDICATION\s+ORDER',
                lambda m, doc: "SEBI Adjudication Order",
                5
            ),
            
            # Pattern 5: Prohibition of Fraudulent regulations
            (
                r'SECURITIES\s+AND\s+EXCHANGE\s+BOARD\s+OF\s+INDIA.*?(PROHIBITION\s+OF\s+FRAUDUL[ENT\s]+AND\s+UNFAIR[^\n]{0,60})',
                lambda m, doc: f"SEBI {m.group(1).strip()[:100]}",
                8
            ),
            
            # Pattern 6: Generic SEBI Regulation
            (
                r'SECURITIES\s+AND\s+EXCHANGE\s+BOARD\s+OF\s+INDIA.*?(\([\w\s]+\)\s+REGULATIONS?,?\s+\d{4})',
                lambda m, doc: f"SEBI {m.group(1).strip()[:100]}",
                7
            ),
            
            # Pattern 7: Circular with reference
            (
                r'CIRCULAR.*?(?:No\.|Number|Ref)[:\s]+([\w/\-]+)',
                lambda m, doc: f"SEBI Circular ({m.group(1)[:30]})",
                6
            ),
            
            # Pattern 8: Guidelines
            (
                r'GUIDELINES?\s+ON\s+(.{20,100})',
                lambda m, doc: f"SEBI Guidelines: {m.group(1).strip()[:80]}",
                6
            ),
        ]
        
        # Sort patterns by priority (highest first)
        self.patterns.sort(key=lambda x: x[2], reverse=True)
        
        # Compile regex patterns for performance
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE | re.DOTALL), formatter, priority)
            for pattern, formatter, priority in self.patterns
        ]
    
    def _format_subject_title(self, subject: str, document: str) -> str:
        """
        Format a subject line into a proper title.
        
        Args:
            subject: Subject line text
            document: Full document for context
            
        Returns:
            Formatted title
        """
        subject = subject.strip()
        
        # Remove common prefixes
        subject = re.sub(r'^Subject\s*:\s*', '', subject, flags=re.IGNORECASE)
        subject = subject.strip()
        
        # Check document type for appropriate prefix
        doc_upper = document[:500].upper()
        
        if 'MASTER CIRCULAR' in doc_upper:
            return f"SEBI Master Circular: {subject[:100]}"
        elif 'CIRCULAR' in doc_upper:
            return f"SEBI Circular: {subject[:100]}"
        elif 'GUIDELINE' in doc_upper:
            return f"SEBI Guidelines: {subject[:100]}"
        else:
            return f"SEBI: {subject[:100]}"
    
    def extract(self, document: str, max_lines: int = 30) -> str:
        """
        Extract title from a document.
        
        Args:
            document: Full document text
            max_lines: Maximum number of lines to search (for performance)
            
        Returns:
            Extracted title or fallback
        """
        if not document or not document.strip():
            return "SEBI Document"
        
        # Extract first N lines for analysis
        lines = document.split('\n')[:max_lines]
        header_text = '\n'.join(lines)
        
        # Try each pattern in priority order
        for pattern, formatter, _ in self.compiled_patterns:
            match = pattern.search(header_text)
            if match:
                try:
                    title = formatter(match, document)
                    # Validate title quality
                    if title and len(title.strip()) > 10:
                        return self._clean_title(title)
                except Exception:
                    # If formatter fails, continue to next pattern
                    continue
        
        # Fallback: Use first substantial line
        return self._extract_fallback_title(lines)
    
    def _clean_title(self, title: str) -> str:
        """
        Clean up extracted title.
        
        Args:
            title: Raw title text
            
        Returns:
            Cleaned title
        """
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title)
        
        # Remove control characters
        title = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', title)
        
        # Trim to reasonable length
        if len(title) > 150:
            title = title[:147] + "..."
        
        return title.strip()
    
    def _extract_fallback_title(self, lines: List[str]) -> str:
        """
        Extract fallback title from lines.
        
        Args:
            lines: Document lines
            
        Returns:
            Fallback title
        """
        for line in lines[:10]:
            cleaned = line.strip()
            # Skip very short lines and common headers
            if len(cleaned) < 20:
                continue
            if cleaned.upper() in ['SEBI', 'NOTIFICATION', 'CIRCULAR', 'GUIDELINES']:
                continue
            # Use first substantial line
            return self._clean_title(cleaned)
        
        return "SEBI Document"
    
    def extract_with_metadata(self, document: str) -> dict:
        """
        Extract title along with metadata about extraction.
        
        Args:
            document: Document text
            
        Returns:
            Dict with title, confidence, and method used
        """
        if not document or not document.strip():
            return {
                'title': "SEBI Document",
                'confidence': 0.0,
                'method': 'empty_document'
            }
        
        lines = document.split('\n')[:30]
        header_text = '\n'.join(lines)
        
        # Try patterns
        for pattern, formatter, priority in self.compiled_patterns:
            match = pattern.search(header_text)
            if match:
                try:
                    title = formatter(match, document)
                    if title and len(title.strip()) > 10:
                        return {
                            'title': self._clean_title(title),
                            'confidence': priority / 10.0,  # Convert priority to confidence
                            'method': 'pattern_match'
                        }
                except Exception:
                    continue
        
        # Fallback
        fallback_title = self._extract_fallback_title(lines)
        return {
            'title': fallback_title,
            'confidence': 0.5 if fallback_title != "SEBI Document" else 0.2,
            'method': 'fallback'
        }

