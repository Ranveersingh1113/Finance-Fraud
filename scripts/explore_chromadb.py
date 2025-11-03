"""
Explore ChromaDB collections to understand document structure and IDs.
This helps you create ground truth labels for evaluation.

Usage:
    python scripts/explore_chromadb.py
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def explore_collection(collection, collection_name: str, limit: int = 50):
    """Explore a single collection and print details."""
    print("=" * 80)
    print(f"COLLECTION: {collection_name}")
    print("=" * 80)
    
    # Get collection count
    count = collection.count()
    print(f"Total documents: {count}\n")
    
    # Get sample documents
    try:
        data = collection.get(
            limit=min(limit, count),
            include=['metadatas', 'documents']
        )
        
        print(f"Showing first {len(data['ids'])} documents:\n")
        
        for i, doc_id in enumerate(data['ids']):
            metadata = data['metadatas'][i]
            document = data['documents'][i]
            
            print(f"[{i+1}] ID: {doc_id}")
            print(f"    Title: {metadata.get('title', 'N/A')[:70]}")
            print(f"    Type: {metadata.get('document_type', 'unknown')}")
            print(f"    Source: {metadata.get('source', 'N/A')}")
            
            # Show other interesting metadata
            if 'violation_types' in metadata and metadata['violation_types']:
                print(f"    Violations: {metadata['violation_types'][:100]}")
            if 'keywords' in metadata and metadata['keywords']:
                print(f"    Keywords: {metadata['keywords'][:100]}")
            
            # Show document preview
            doc_preview = document[:150].replace('\n', ' ')
            print(f"    Preview: {doc_preview}...")
            print()
        
        # Document type distribution
        doc_types = {}
        for metadata in data['metadatas']:
            doc_type = metadata.get('document_type', 'unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        print(f"\n[STATS] DOCUMENT TYPE DISTRIBUTION:")
        for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {doc_type}: {count} documents")
        
    except Exception as e:
        print(f"Error exploring collection: {e}")
    
    print()


def search_by_keyword(collection, collection_name: str, keyword: str, n_results: int = 5):
    """Search collection by keyword to find relevant documents."""
    print("=" * 80)
    print(f"KEYWORD SEARCH: '{keyword}' in {collection_name}")
    print("=" * 80)
    
    try:
        # Simple keyword search (not semantic)
        data = collection.get(
            include=['metadatas', 'documents'],
            limit=1000  # Get all to filter
        )
        
        # Filter by keyword
        matches = []
        for i, doc_id in enumerate(data['ids']):
            document = data['documents'][i]
            metadata = data['metadatas'][i]
            
            # Check if keyword appears in document or metadata
            doc_text = document.lower()
            metadata_text = str(metadata).lower()
            
            if keyword.lower() in doc_text or keyword.lower() in metadata_text:
                matches.append({
                    'id': doc_id,
                    'metadata': metadata,
                    'document': document
                })
        
        print(f"Found {len(matches)} documents containing '{keyword}'\n")
        
        # Show top matches
        for i, match in enumerate(matches[:n_results]):
            print(f"[{i+1}] ID: {match['id']}")
            print(f"    Title: {match['metadata'].get('title', 'N/A')[:70]}")
            print(f"    Type: {match['metadata'].get('document_type', 'unknown')}")
            
            # Find keyword context
            doc_lower = match['document'].lower()
            keyword_pos = doc_lower.find(keyword.lower())
            if keyword_pos != -1:
                context_start = max(0, keyword_pos - 50)
                context_end = min(len(match['document']), keyword_pos + len(keyword) + 50)
                context = match['document'][context_start:context_end]
                print(f"    Context: ...{context}...")
            print()
        
    except Exception as e:
        print(f"Error searching collection: {e}")
    
    print()


def main():
    """Main exploration function."""
    print("\n" + "=" * 80)
    print("CHROMADB EXPLORATION TOOL")
    print("=" * 80)
    print()
    
    # Initialize ChromaDB
    try:
        client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        print("[OK] Connected to ChromaDB\n")
    except Exception as e:
        print(f"[ERROR] Failed to connect to ChromaDB: {e}")
        return
    
    # List all collections
    try:
        collections = client.list_collections()
        print(f"Found {len(collections)} collections:")
        for col in collections:
            print(f"  • {col.name}")
        print()
    except Exception as e:
        print(f"Error listing collections: {e}")
        return
    
    # Explore each collection
    for collection_obj in collections:
        explore_collection(collection_obj, collection_obj.name, limit=20)
    
    # Keyword searches to help identify relevant documents
    print("\n" + "=" * 80)
    print("KEYWORD SEARCHES (to help create ground truth labels)")
    print("=" * 80)
    print()
    
    keywords_to_search = [
        "insider trading",
        "money laundering",
        "market manipulation",
        "PMLA",
        "LODR",
        "PFUTP",
        "fan-out",
        "fraud"
    ]
    
    for collection_obj in collections:
        for keyword in keywords_to_search:
            search_by_keyword(collection_obj, collection_obj.name, keyword, n_results=3)
    
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Review the document IDs and types above")
    print("2. Create ground truth labels by mapping queries to relevant doc IDs")
    print("3. Update scripts/measure_baseline_performance.py with real doc IDs")
    print("4. Run: python scripts/measure_baseline_performance.py")
    print()


if __name__ == "__main__":
    main()

