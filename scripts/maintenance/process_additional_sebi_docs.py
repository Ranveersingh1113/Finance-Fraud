"""
Process Additional SEBI Documents and Update Knowledge Base
Processes PDFs from data/additional_sebi and updates:
1. SEBI Knowledge Graph
2. ChromaDB Vector Store
"""
import sys
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path (go up 2 levels from scripts/maintenance/)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.sebi_file_processor import SEBIFileProcessor
from src.data.sebi_processor import SEBIProcessor
from src.data.entity_extractor import EntityExtractor
from src.core.sebi_graph_manager import SEBIGraphManager
from src.core.advanced_rag_engine import AdvancedRAGEngine

def print_section(title: str):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"{title}")
    print("="*70)

def main():
    """Process additional SEBI documents and update the knowledge base."""
    
    print_section("Processing Additional SEBI Documents")
    print("Location: data/additional_sebi/")
    
    # Initialize processors
    print("\n[Step 1] Initializing processors...")
    sebi_file_processor = SEBIFileProcessor(sebi_directory="./data/additional_sebi")
    sebi_processor = SEBIProcessor()
    entity_extractor = EntityExtractor()
    
    # Increase spaCy max_length to handle large documents
    entity_extractor.nlp.max_length = 2000000  # 2 million characters
    
    print("  [OK] Processors initialized")
    
    # Process files
    print("\n[Step 2] Processing PDF files...")
    documents = sebi_file_processor.process_all_files()
    
    if not documents:
        print("  [ERROR] No documents processed!")
        return
    
    print(f"  [OK] Processed {len(documents)} documents")
    
    # Show document types
    doc_types = {}
    for doc in documents:
        doc_type = doc.document_type
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
    
    print("\n  Document Types:")
    for doc_type, count in doc_types.items():
        print(f"    - {doc_type}: {count}")
    
    # Convert to chunks
    print("\n[Step 3] Creating document chunks...")
    doc_dicts = []
    for doc in documents:
        doc_dict = {
            'document_id': doc.document_id,
            'title': doc.title,
            'document_type': doc.document_type,
            'url': doc.file_path,
            'date': doc.date.isoformat() if doc.date else None,
            'content': doc.content,
            'metadata': doc.metadata
        }
        doc_dicts.append(doc_dict)
    
    chunks = sebi_processor.process_documents(doc_dicts)
    print(f"  [OK] Created {len(chunks)} chunks")
    
    # Update knowledge graph
    print("\n[Step 4] Updating SEBI Knowledge Graph...")
    
    # Load existing graph
    graph_path = Path("data/graphs/sebi_knowledge_graph.gpickle")
    if graph_path.exists():
        print("  - Loading existing graph...")
        graph_manager = SEBIGraphManager()
        graph_manager.load_graph(str(graph_path))
        initial_nodes = graph_manager.graph.number_of_nodes()
        initial_edges = graph_manager.graph.number_of_edges()
        print(f"    Initial state: {initial_nodes} nodes, {initial_edges} edges")
    else:
        print("  - Creating new graph...")
        graph_manager = SEBIGraphManager()
        initial_nodes = 0
        initial_edges = 0
    
    # Process each chunk for entity extraction
    print("  - Extracting entities and relationships...")
    entities_added = 0
    relationships_added = 0
    
    for i, chunk in enumerate(chunks):
        if (i + 1) % 50 == 0:
            print(f"    Processed {i + 1}/{len(chunks)} chunks...")
        
        # Extract entities and relationships
        entities = entity_extractor.extract_entities(chunk.content)
        relationships = entity_extractor.extract_relationships(chunk.content, entities)
        
        # Add to graph
        for entity in entities:
            graph_manager.add_node(
                node_id=entity.text,
                node_type=entity.entity_type,
                properties={
                    'source_document': chunk.document_id,
                    'chunk_id': chunk.chunk_id,
                    'entity_type': entity.entity_type,
                    'confidence': entity.confidence
                }
            )
            entities_added += 1
        
        for rel in relationships:
            graph_manager.add_edge(
                source_id=rel.source,
                target_id=rel.target,
                relationship=rel.relationship_type,
                source_document=chunk.document_id,
                chunk_id=chunk.chunk_id,
                context=rel.context,
                confidence=rel.confidence
            )
            relationships_added += 1
    
    final_nodes = graph_manager.graph.number_of_nodes()
    final_edges = graph_manager.graph.number_of_edges()
    
    print(f"\n  Graph Update Summary:")
    print(f"    New entities: {entities_added}")
    print(f"    New relationships: {relationships_added}")
    print(f"    Total nodes: {initial_nodes} -> {final_nodes} (+{final_nodes - initial_nodes})")
    print(f"    Total edges: {initial_edges} -> {final_edges} (+{final_edges - initial_edges})")
    
    # Save updated graph
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_manager.save_graph(str(graph_path))
    print(f"  [OK] Saved updated graph to {graph_path}")
    
    # Update ChromaDB
    print("\n[Step 5] Updating ChromaDB Vector Store...")
    
    try:
        # Initialize RAG engine (connects to existing collections)
        rag_engine = AdvancedRAGEngine(persist_directory="./data/chroma_db")
        
        print("  - Connected to SEBI collection")
        
        # Get current collection stats
        try:
            existing_count = rag_engine.sebi_collection.count()
            print(f"    Current documents: {existing_count}")
        except:
            existing_count = 0
            print("    Current documents: 0 (new collection)")
        
        # Prepare documents for indexing
        texts = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            texts.append(chunk.content)
            
            # Prepare metadata (ChromaDB compatible - only str, int, float, bool)
            metadata = {
                'document_id': str(chunk.document_id),
                'chunk_id': str(chunk.chunk_id),
                'document_type': str(chunk.document_type),
                'title': str(chunk.title)[:200] if chunk.title else '',  # Limit length
                'chunk_index': int(chunk.chunk_index),
                'url': str(chunk.url) if chunk.url else '',
                'keywords': ','.join(chunk.keywords[:10]) if chunk.keywords else '',  # Limit
                'entities': ','.join(chunk.entities[:10]) if chunk.entities else '',  # Limit
                'violations': ','.join(chunk.violation_types[:5]) if chunk.violation_types else ''  # Limit
            }
            
            # Add date if available
            if chunk.date:
                # chunk.date might already be a string or datetime
                if hasattr(chunk.date, 'isoformat'):
                    metadata['date'] = chunk.date.isoformat()
                else:
                    metadata['date'] = str(chunk.date)
            
            metadatas.append(metadata)
            ids.append(chunk.chunk_id)
        
        # Add to collection
        print(f"  - Adding {len(texts)} new chunks to ChromaDB...")
        rag_engine.sebi_collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        new_count = rag_engine.sebi_collection.count()
        print(f"  [OK] ChromaDB updated: {existing_count} -> {new_count} (+{new_count - existing_count})")
        
    except Exception as e:
        print(f"  [WARNING] ChromaDB update failed: {e}")
        print("  You may need to re-index manually")
    
    # Final summary
    print_section("Processing Complete!")
    
    print(f"""
Summary:
  Documents Processed: {len(documents)}
  Chunks Created: {len(chunks)}
  
  Knowledge Graph:
    Nodes: {initial_nodes} -> {final_nodes} (+{final_nodes - initial_nodes})
    Edges: {initial_edges} -> {final_edges} (+{final_edges - initial_edges})
  
  Vector Store:
    Chunks: {existing_count} -> {new_count} (+{new_count - existing_count})

Next Steps:
  1. Test queries with enhanced regulatory coverage
  2. Verify cross-domain pattern matching improvements
  3. Proceed with Phase 4 UI integration

Files Updated:
  - {graph_path}
  - data/chroma_db/ (vector store)
""")
    
    print("="*70)

if __name__ == "__main__":
    main()

