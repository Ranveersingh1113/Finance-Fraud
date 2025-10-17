"""
SEBI Knowledge Graph Manager for Financial Intelligence Platform.
Builds regulatory knowledge graph from SEBI enforcement documents.
Phase 4: GraphRAG & Network Intelligence - Week 1-2
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import json

from .graph_manager import GraphManager
from ..data.entity_extractor import EntityExtractor, Entity, Relationship

try:
    from ..data.sebi_processor import ProcessedChunk
except ImportError:
    from data.sebi_processor import ProcessedChunk

logger = logging.getLogger(__name__)


class SEBIGraphManager(GraphManager):
    """
    SEBI-specific knowledge graph manager.
    
    Node Types:
    - Entity: Companies, individuals involved in violations
    - Violation: Types of fraud/regulatory violations
    - Regulator: SEBI, RBI, etc.
    - Document: SEBI orders, reports
    - Penalty: Financial penalties imposed
    
    Relationship Types:
    - COMMITTED: Entity → Violation
    - PENALIZED_BY: Entity → Regulator
    - CITED_IN: Entity → Document
    - SIMILAR_TO: Violation → Violation
    - IMPOSED: Regulator → Penalty
    - RECEIVED: Entity → Penalty
    """
    
    def __init__(self, persist_directory: str = "./data/graphs"):
        """
        Initialize SEBI knowledge graph manager.
        
        Args:
            persist_directory: Directory to save/load graphs
        """
        super().__init__(
            graph_name="sebi_knowledge_graph",
            persist_directory=persist_directory
        )
        
        # Initialize entity extractor
        self.entity_extractor = EntityExtractor()
        
        # Statistics
        self.processed_documents = 0
        self.extracted_entities = 0
        self.extracted_relationships = 0
        
        logger.info("SEBI Knowledge Graph Manager initialized")
    
    def process_sebi_document(self, document: ProcessedChunk) -> Dict[str, Any]:
        """
        Process a SEBI document and add to knowledge graph.
        
        Args:
            document: Processed SEBI document chunk
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Extract entities and relationships
            extraction_result = self.entity_extractor.extract_from_document(
                document.content,
                doc_id=document.chunk_id
            )
            
            # Add document node
            doc_node_id = f"doc_{document.document_id}_{document.chunk_index}"
            self.add_node(
                doc_node_id,
                "Document",
                title=document.title,
                document_type=document.document_type,
                chunk_id=document.chunk_id,
                chunk_index=document.chunk_index,
                date=str(document.date) if document.date else None,
                url=document.url,
                content_preview=document.content[:200]
            )
            
            # Process extracted entities
            entity_nodes = []
            for entity in extraction_result['entities']:
                entity_node_id = self._add_entity_node(
                    entity,
                    document_id=doc_node_id
                )
                entity_nodes.append(entity_node_id)
            
            # Process extracted relationships
            for relationship in extraction_result['relationships']:
                self._add_relationship_edge(
                    relationship,
                    document_id=doc_node_id
                )
            
            # Add metadata-based entities
            self._process_document_metadata(document, doc_node_id)
            
            # Update statistics
            self.processed_documents += 1
            self.extracted_entities += len(extraction_result['entities'])
            self.extracted_relationships += len(extraction_result['relationships'])
            
            logger.info(f"Processed document {document.chunk_id}: "
                       f"{len(extraction_result['entities'])} entities, "
                       f"{len(extraction_result['relationships'])} relationships")
            
            return {
                'doc_id': doc_node_id,
                'entities_added': len(entity_nodes),
                'relationships_added': len(extraction_result['relationships']),
                'extraction_summary': extraction_result['summary']
            }
            
        except Exception as e:
            logger.error(f"Error processing SEBI document: {e}")
            return {
                'doc_id': None,
                'entities_added': 0,
                'relationships_added': 0,
                'error': str(e)
            }
    
    def process_sebi_documents_batch(self, documents: List[ProcessedChunk]) -> Dict[str, Any]:
        """
        Process multiple SEBI documents in batch.
        
        Args:
            documents: List of processed SEBI document chunks
            
        Returns:
            Batch processing statistics
        """
        results = []
        total_entities = 0
        total_relationships = 0
        errors = 0
        
        logger.info(f"Processing batch of {len(documents)} SEBI documents...")
        
        for i, doc in enumerate(documents):
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i + 1}/{len(documents)} documents processed")
            
            result = self.process_sebi_document(doc)
            results.append(result)
            
            if 'error' in result:
                errors += 1
            else:
                total_entities += result['entities_added']
                total_relationships += result['relationships_added']
        
        logger.info(f"Batch processing complete: {len(documents)} documents, "
                   f"{total_entities} entities, {total_relationships} relationships, "
                   f"{errors} errors")
        
        return {
            'documents_processed': len(documents),
            'total_entities': total_entities,
            'total_relationships': total_relationships,
            'errors': errors,
            'results': results
        }
    
    def _add_entity_node(self, entity: Entity, document_id: str) -> str:
        """
        Add an entity node to the graph.
        
        Args:
            entity: Extracted entity
            document_id: Source document node ID
            
        Returns:
            Entity node ID
        """
        # Create normalized entity ID
        entity_id = self._normalize_entity_id(entity.text, entity.entity_type)
        
        # Check if entity already exists
        existing_node = self.get_node(entity_id)
        
        if existing_node:
            # Update citation count
            citation_count = existing_node.get('citation_count', 1) + 1
            self.graph.nodes[entity_id]['citation_count'] = citation_count
            
            # Add document reference
            if 'documents' not in self.graph.nodes[entity_id]:
                self.graph.nodes[entity_id]['documents'] = []
            if document_id not in self.graph.nodes[entity_id]['documents']:
                self.graph.nodes[entity_id]['documents'].append(document_id)
        else:
            # Add new entity node
            self.add_node(
                entity_id,
                entity.entity_type,
                name=entity.text,
                confidence=entity.confidence,
                citation_count=1,
                documents=[document_id],
                context=entity.context
            )
        
        # Add CITED_IN relationship to document
        self.add_edge(
            entity_id,
            document_id,
            "CITED_IN",
            confidence=entity.confidence
        )
        
        return entity_id
    
    def _add_relationship_edge(self, relationship: Relationship, document_id: str) -> None:
        """
        Add a relationship edge to the graph.
        
        Args:
            relationship: Extracted relationship
            document_id: Source document node ID
        """
        # Normalize entity IDs
        source_id = self._normalize_entity_id(
            relationship.source,
            relationship.source_type
        )
        target_id = self._normalize_entity_id(
            relationship.target,
            relationship.target_type
        )
        
        # Ensure both entities exist as nodes
        if source_id not in self.graph:
            self.add_node(
                source_id,
                relationship.source_type,
                name=relationship.source,
                citation_count=1,
                documents=[document_id]
            )
        
        if target_id not in self.graph:
            self.add_node(
                target_id,
                relationship.target_type,
                name=relationship.target,
                citation_count=1,
                documents=[document_id]
            )
        
        # Add relationship edge
        self.add_edge(
            source_id,
            target_id,
            relationship.relationship_type,
            confidence=relationship.confidence,
            source_document=document_id,
            context=relationship.context
        )
    
    def _process_document_metadata(self, document: ProcessedChunk, doc_node_id: str) -> None:
        """
        Process document metadata and add structured entities.
        
        Args:
            document: Processed SEBI document
            doc_node_id: Document node ID
        """
        # Add violation types from metadata
        for violation_type in document.violation_types:
            violation_id = self._normalize_entity_id(violation_type, "Violation")
            
            if violation_id not in self.graph:
                self.add_node(
                    violation_id,
                    "Violation",
                    name=violation_type,
                    citation_count=1,
                    documents=[doc_node_id]
                )
            else:
                # Update citation count
                self.graph.nodes[violation_id]['citation_count'] = \
                    self.graph.nodes[violation_id].get('citation_count', 1) + 1
            
            # Link document to violation
            self.add_edge(
                doc_node_id,
                violation_id,
                "DESCRIBES",
                source="metadata"
            )
        
        # Add entities from metadata
        for entity_name in document.entities:
            entity_id = self._normalize_entity_id(entity_name, "Entity")
            
            if entity_id not in self.graph:
                self.add_node(
                    entity_id,
                    "Entity",
                    name=entity_name,
                    citation_count=1,
                    documents=[doc_node_id]
                )
            else:
                self.graph.nodes[entity_id]['citation_count'] = \
                    self.graph.nodes[entity_id].get('citation_count', 1) + 1
            
            # Link entity to document
            self.add_edge(
                entity_id,
                doc_node_id,
                "CITED_IN",
                source="metadata"
            )
    
    def _normalize_entity_id(self, entity_text: str, entity_type: str) -> str:
        """
        Create normalized entity ID.
        
        Args:
            entity_text: Entity text
            entity_type: Entity type
            
        Returns:
            Normalized entity ID
        """
        # Clean and normalize text
        normalized_text = entity_text.lower().strip()
        normalized_text = normalized_text.replace(" ", "_")
        normalized_text = ''.join(c for c in normalized_text if c.isalnum() or c == '_')
        
        return f"{entity_type}_{normalized_text}"
    
    def find_entity_violations(self, entity_name: str) -> List[Dict]:
        """
        Find all violations associated with an entity.
        
        Args:
            entity_name: Entity name to search
            
        Returns:
            List of violations with details
        """
        entity_id = self._normalize_entity_id(entity_name, "Entity")
        
        if entity_id not in self.graph:
            return []
        
        violations = []
        
        # Get all neighbors
        for neighbor in self.graph.neighbors(entity_id):
            neighbor_data = self.get_node(neighbor)
            
            if neighbor_data and neighbor_data.get('type') == 'Violation':
                # Get relationship details
                edges = self.graph[entity_id][neighbor]
                for edge_data in edges.values():
                    violations.append({
                        'violation': neighbor_data.get('name'),
                        'violation_id': neighbor,
                        'relationship': edge_data.get('relationship'),
                        'confidence': edge_data.get('confidence', 0),
                        'context': edge_data.get('context', '')
                    })
        
        return violations
    
    def find_similar_cases(self, violation_type: str, limit: int = 5) -> List[Dict]:
        """
        Find cases with similar violations.
        
        Args:
            violation_type: Type of violation to search
            limit: Maximum number of results
            
        Returns:
            List of similar cases
        """
        violation_id = self._normalize_entity_id(violation_type, "Violation")
        
        if violation_id not in self.graph:
            return []
        
        # Find all entities that committed this violation
        similar_cases = []
        
        for node in self.graph:
            node_data = self.get_node(node)
            if node_data and node_data.get('type') == 'Entity':
                # Check if this entity has the violation
                violations = self.find_entity_violations(node_data.get('name', ''))
                for v in violations:
                    if v['violation'].lower() == violation_type.lower():
                        similar_cases.append({
                            'entity': node_data.get('name'),
                            'entity_id': node,
                            'violation': v['violation'],
                            'citation_count': node_data.get('citation_count', 0),
                            'documents': node_data.get('documents', [])
                        })
        
        # Sort by citation count (more citations = more significant)
        similar_cases.sort(key=lambda x: x['citation_count'], reverse=True)
        
        return similar_cases[:limit]
    
    def get_sebi_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about SEBI knowledge graph.
        
        Returns:
            Dictionary with statistics
        """
        base_stats = self.get_statistics()
        
        # Count entities by type
        entity_count = len(self.find_nodes_by_type('Entity'))
        violation_count = len(self.find_nodes_by_type('Violation'))
        document_count = len(self.find_nodes_by_type('Document'))
        regulator_count = len(self.find_nodes_by_type('Regulator'))
        penalty_count = len(self.find_nodes_by_type('Penalty'))
        
        # Find most cited entities
        entities = [(node, data.get('citation_count', 0)) 
                   for node, data in self.graph.nodes(data=True)
                   if data.get('type') == 'Entity']
        top_entities = sorted(entities, key=lambda x: x[1], reverse=True)[:10]
        
        # Find most common violations
        violations = [(node, data.get('citation_count', 0))
                     for node, data in self.graph.nodes(data=True)
                     if data.get('type') == 'Violation']
        top_violations = sorted(violations, key=lambda x: x[1], reverse=True)[:10]
        
        return {
            **base_stats,
            'sebi_specific': {
                'entities': entity_count,
                'violations': violation_count,
                'documents': document_count,
                'regulators': regulator_count,
                'penalties': penalty_count,
                'processed_documents': self.processed_documents,
                'extracted_entities': self.extracted_entities,
                'extracted_relationships': self.extracted_relationships
            },
            'top_entities': [
                {'id': eid, 'name': self.get_node(eid).get('name'), 'citations': count}
                for eid, count in top_entities
            ],
            'top_violations': [
                {'id': vid, 'name': self.get_node(vid).get('name'), 'citations': count}
                for vid, count in top_violations
            ]
        }
    
    def export_for_visualization(self, output_path: str = None) -> str:
        """
        Export graph in format suitable for visualization.
        
        Args:
            output_path: Optional output path
            
        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = self.persist_directory / "sebi_graph_visualization.json"
        
        # Create visualization-friendly format
        nodes = []
        edges = []
        
        # Process nodes
        for node_id, node_data in self.graph.nodes(data=True):
            nodes.append({
                'id': node_id,
                'label': node_data.get('name', node_id),
                'type': node_data.get('type', 'Unknown'),
                'citations': node_data.get('citation_count', 0),
                'group': node_data.get('type', 'Unknown')
            })
        
        # Process edges
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                'from': source,
                'to': target,
                'label': data.get('relationship', 'RELATED'),
                'confidence': data.get('confidence', 1.0)
            })
        
        viz_data = {
            'nodes': nodes,
            'edges': edges,
            'statistics': self.get_sebi_statistics(),
            'metadata': {
                'graph_type': 'sebi_knowledge_graph',
                'created_at': self.created_at,
                'last_updated': self.last_updated
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(viz_data, f, indent=2)
        
        logger.info(f"Graph exported for visualization: {output_path}")
        return str(output_path)

