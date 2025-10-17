"""
Entity Extractor for Financial Intelligence Platform.
Extracts entities and relationships from financial documents using NLP.
Phase 4: GraphRAG & Network Intelligence
"""
import spacy
from typing import List, Dict, Any, Tuple, Set
import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Extracted entity with metadata."""
    text: str
    entity_type: str
    start: int
    end: int
    confidence: float = 1.0
    context: str = ""


@dataclass
class Relationship:
    """Extracted relationship between entities."""
    source: str
    source_type: str
    relationship_type: str
    target: str
    target_type: str
    confidence: float = 1.0
    context: str = ""


class EntityExtractor:
    """
    Extract entities and relationships from financial documents.
    
    Uses spaCy NLP + custom rules for financial domain.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize entity extractor.
        
        Args:
            model_name: spaCy model to use
        """
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.error(f"Model {model_name} not found. Run: python -m spacy download {model_name}")
            raise
        
        # Entity stopwords - Filter out generic/legal terms
        self.entity_stopwords = {
            'inter alia', 'individuals', 'companies', 'parties', 'entities',
            'persons', 'appellant', 'respondent', 'petitioner', 'noticee',
            'scn', 'etc', 'viz', 'vide', 'ibid', 'supra', 'infra',
            'show cause notice', 'interim order', 'final order',
            'adjudication order', 'settlement order', 'consent order',
            'applicant', 'appellee', 'claimant', 'defendant',
            'case', 'matter', 'proceedings', 'order', 'notice',
            'regulation', 'provision', 'clause', 'section', 'act',
            'board', 'tribunal', 'authority', 'commission',
            'the company', 'the entity', 'the person', 'the individual',
            'said', 'same', 'aforesaid', 'aforementioned'
        }
        
        # Financial domain patterns
        self.violation_patterns = [
            "insider trading", "market manipulation", "price rigging",
            "wash trading", "front running", "churning", "pump and dump",
            "ponzi scheme", "fraud", "misrepresentation", "disclosure violation",
            "circular trading", "matched orders", "fictitious trades",
            "false market", "spoofing", "layering", "corporate governance",
            "money laundering", "unfair trade practice", "market abuse"
        ]
        
        self.penalty_patterns = [
            r"₹\s*\d+(?:,\d+)*(?:\.\d+)?\s*(?:lakh|crore|L|Cr)?",
            r"INR\s*\d+(?:,\d+)*(?:\.\d+)?",
            r"penalty of ₹[\d,.]+"
        ]
        
        self.relationship_patterns = {
            'COMMITTED': [
                r"([A-Z][A-Za-z\s&]+?(?:Ltd|Limited|Corporation|Corp|Inc)?\.?)\s+(?:committed|involved in|engaged in|indulged in)\s+(insider trading|fraud|market manipulation|[\w\s]+violation)",
                r"([A-Z][A-Za-z\s&]+?)\s+(?:was |were )?(?:found )?guilty of\s+(insider trading|fraud|market manipulation|[\w\s]+)",
                r"([A-Z][A-Za-z\s&]+?)\s+(?:has |have )?violated\s+",
                r"violation(?:s)? (?:by|of)\s+([A-Z][A-Za-z\s&]+?)\s+"
            ],
            'PENALIZED_BY': [
                r"([A-Z][A-Za-z\s&]+?(?:Ltd|Limited|Corporation|Corp|Inc)?\.?)\s+(?:was |were )?(?:directed to pay|imposed with|penalized)\s+.*?(?:by\s+)?(SEBI|Securities and Exchange Board)",
                r"(SEBI|Securities and Exchange Board).*?(?:imposed|directed|ordered)\s+.*?(?:penalty|fine|disgorgement)\s+(?:on|upon)\s+([A-Z][A-Za-z\s&]+)",
                r"(SEBI|Securities and Exchange Board).*?(?:penalized|sanctioned)\s+([A-Z][A-Za-z\s&]+)",
                r"([A-Z][A-Za-z\s&]+?)\s+(?:shall pay|directed to pay|ordered to pay).*?penalty",
                r"penalty.*?imposed on\s+([A-Z][A-Za-z\s&]+)"
            ],
            'SIMILAR_TO': [
                r"similar to\s+(?:case\s+)?(?:no\.?\s*)?([A-Z]+[/-]\d+[/-]\d+)",
                r"(?:akin|comparable|analogous) to\s+(?:the )?case\s+(?:of\s+)?([A-Z][A-Za-z\s&]+)",
                r"(?:in line with|consistent with|following)\s+(?:case\s+)?([A-Z]+[/-]\d+)",
                r"(?:vide|reference to|as in)\s+(?:case\s+)?(?:no\.?\s*)?([A-Z]+[/-]\d+)"
            ],
            'RECEIVED_PENALTY': [
                r"([A-Z][A-Za-z\s&]+?(?:Ltd|Limited)?\.?)\s+(?:was directed to pay|shall pay|ordered to pay)\s+(₹[\d,]+\s*(?:lakh|crore)?)",
                r"penalty of\s+(₹[\d,]+\s*(?:lakh|crore)?)\s+(?:on|imposed on|upon)\s+([A-Z][A-Za-z\s&]+)"
            ]
        }
    
    def should_keep_entity(self, entity: Entity) -> bool:
        """
        Determine if an entity should be kept based on quality criteria.
        
        Args:
            entity: Entity to evaluate
            
        Returns:
            True if entity should be kept
        """
        # Always keep high-priority types
        if entity.entity_type in ['Violation', 'Penalty', 'Regulator']:
            return True
        
        # Filter dates - only keep if they look like violation/order dates
        if entity.entity_type == 'Date':
            # Keep dates mentioned near keywords
            context_lower = entity.context.lower()
            date_keywords = ['order', 'violation', 'penalty', 'dated', 'adjudication', 'enforcement']
            if any(keyword in context_lower for keyword in date_keywords):
                return True
            return False  # Skip most dates
        
        # Filter numbers - only keep if they look like amounts/penalties
        if entity.entity_type == 'Number':
            # Keep if near money-related terms
            context_lower = entity.context.lower()
            number_keywords = ['₹', 'rupees', 'lakh', 'crore', 'penalty', 'fine', 'amount', 'rs']
            if any(keyword in context_lower for keyword in number_keywords):
                return True
            return False  # Skip most numbers
        
        # Keep entities and persons
        return True
    
    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract entities from text with quality filtering.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted high-quality entities
        """
        entities = []
        doc = self.nlp(text)
        
        # Extract named entities using spaCy
        for ent in doc.ents:
            # Skip stopwords
            if ent.text.lower() in self.entity_stopwords:
                continue
            
            # Skip very short entities (likely artifacts)
            if len(ent.text) < 3:
                continue
            
            # Map spaCy entity types to our domain
            entity_type = self._map_entity_type(ent.label_)
            
            if entity_type:
                entities.append(Entity(
                    text=ent.text,
                    entity_type=entity_type,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.8,  # Base confidence for spaCy NER
                    context=text[max(0, ent.start_char-50):min(len(text), ent.end_char+50)]
                ))
        
        # Extract violation types using patterns
        for violation in self.violation_patterns:
            for match in re.finditer(violation, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    entity_type='Violation',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9,  # High confidence for pattern matches
                    context=text[max(0, match.start()-50):min(len(text), match.end()+50)]
                ))
        
        # Extract penalties
        for pattern in self.penalty_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(),
                    entity_type='Penalty',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95,
                    context=text[max(0, match.start()-50):min(len(text), match.end()+50)]
                ))
        
        # Extract company names (additional patterns)
        company_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Ltd\.|Limited|Corporation|Corp\.|Inc\.|Private Limited|Pvt\.?\s*Ltd\.?)',
            r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+)\s+(?:Ltd\.|Limited)',
            r'([A-Z][A-Z]+)\s+(?:Ltd\.|Limited|Corporation|Corp\.)',  # All caps company names
        ]
        
        for pattern in company_patterns:
            for match in re.finditer(pattern, text):
                company_name = match.group()
                
                # Skip if in stopwords
                if company_name.lower() in self.entity_stopwords:
                    continue
                
                # Skip single word companies (usually artifacts)
                if len(company_name.split()) < 2 and not company_name.isupper():
                    continue
                
                entities.append(Entity(
                    text=company_name,
                    entity_type='Entity',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.85,
                    context=text[max(0, match.start()-50):min(len(text), match.end()+50)]
                ))
        
        # Deduplicate entities (prefer higher confidence)
        entities = self._deduplicate_entities(entities)
        
        # Apply quality filtering
        filtered_entities = [e for e in entities if self.should_keep_entity(e)]
        
        logger.info(f"Extracted {len(filtered_entities)} entities (filtered from {len(entities)})")
        return filtered_entities
    
    def extract_relationships(self, text: str, entities: List[Entity] = None) -> List[Relationship]:
        """
        Extract relationships between entities.
        
        Args:
            text: Input text
            entities: Optional list of pre-extracted entities
            
        Returns:
            List of extracted relationships
        """
        if entities is None:
            entities = self.extract_entities(text)
        
        relationships = []
        
        # Extract relationships using patterns
        for rel_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    if match.groups():
                        if len(match.groups()) >= 2:
                            source = match.group(1).strip()
                            target = match.group(2).strip()
                        else:
                            # For patterns with single capture (SIMILAR_TO)
                            source = "current_case"
                            target = match.group(1).strip()
                        
                        # Determine entity types
                        source_type = self._infer_entity_type(source, entities)
                        target_type = self._infer_entity_type(target, entities)
                        
                        relationships.append(Relationship(
                            source=source,
                            source_type=source_type,
                            relationship_type=rel_type,
                            target=target,
                            target_type=target_type,
                            confidence=0.7,
                            context=text[max(0, match.start()-100):min(len(text), match.end()+100)]
                        ))
        
        logger.info(f"Extracted {len(relationships)} relationships")
        return relationships
    
    def extract_from_document(self, document: str, doc_id: str = None) -> Dict[str, Any]:
        """
        Extract all entities and relationships from a document.
        
        Args:
            document: Document text
            doc_id: Optional document identifier
            
        Returns:
            Dictionary with entities, relationships, and metadata
        """
        entities = self.extract_entities(document)
        relationships = self.extract_relationships(document, entities)
        
        # Group entities by type
        entities_by_type = {}
        for entity in entities:
            if entity.entity_type not in entities_by_type:
                entities_by_type[entity.entity_type] = []
            entities_by_type[entity.entity_type].append(entity.text)
        
        return {
            'doc_id': doc_id,
            'entities': entities,
            'relationships': relationships,
            'entities_by_type': entities_by_type,
            'entity_count': len(entities),
            'relationship_count': len(relationships),
            'summary': {
                'companies': len(entities_by_type.get('Entity', [])),
                'violations': len(entities_by_type.get('Violation', [])),
                'penalties': len(entities_by_type.get('Penalty', [])),
                'people': len(entities_by_type.get('Person', [])),
                'organizations': len(entities_by_type.get('Organization', []))
            }
        }
    
    def _map_entity_type(self, spacy_label: str) -> str:
        """
        Map spaCy entity labels to our domain-specific types.
        
        Args:
            spacy_label: spaCy NER label
            
        Returns:
            Domain-specific entity type or None
        """
        mapping = {
            'ORG': 'Entity',  # Organizations/Companies
            'PERSON': 'Person',
            'GPE': 'Location',  # Geopolitical entities
            'MONEY': 'Penalty',
            'DATE': 'Date',
            'CARDINAL': 'Number',
            'LAW': 'Regulation'
        }
        return mapping.get(spacy_label)
    
    def _infer_entity_type(self, entity_text: str, entities: List[Entity]) -> str:
        """
        Infer entity type from text and extracted entities.
        
        Args:
            entity_text: Entity text
            entities: List of extracted entities
            
        Returns:
            Inferred entity type
        """
        # Check if entity is in our extracted list
        for entity in entities:
            if entity.text.lower() == entity_text.lower():
                return entity.entity_type
        
        # Heuristic inference
        if entity_text.lower() in ['sebi', 'rbi', 'irdai', 'pfrda']:
            return 'Regulator'
        elif any(word in entity_text.lower() for word in self.violation_patterns):
            return 'Violation'
        elif entity_text[0].isupper():
            return 'Entity'
        else:
            return 'Unknown'
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Remove duplicate entities, keeping higher confidence ones.
        
        Args:
            entities: List of entities
            
        Returns:
            Deduplicated list
        """
        # Group by text (case-insensitive)
        entity_groups = {}
        for entity in entities:
            key = entity.text.lower()
            if key not in entity_groups:
                entity_groups[key] = []
            entity_groups[key].append(entity)
        
        # Keep highest confidence entity from each group
        deduplicated = []
        for group in entity_groups.values():
            best_entity = max(group, key=lambda e: e.confidence)
            deduplicated.append(best_entity)
        
        return deduplicated

