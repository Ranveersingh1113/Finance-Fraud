"""
Cleanup script to remove old ChromaDB collections with incorrect embeddings.

This script identifies and optionally removes:
1. Old baseline collections (sebi_documents, transactions) 
2. Any collections with incorrect embeddings from before the fix

After running this, you should only have:
- sebi_documents_advanced (corrected, 4,047 chunks)
- amlsim_transactions (correct, 10,401 documents)
- transactions_advanced (if used, should be empty)
"""

import chromadb
from pathlib import Path
from chromadb.config import Settings as ChromaSettings

def analyze_collections():
    """Analyze all ChromaDB collections and identify which to keep/delete."""
    
    chroma_path = Path("data/chroma_db")
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=ChromaSettings(anonymized_telemetry=False)
    )
    
    print("=" * 70)
    print("CHROMADB COLLECTION ANALYSIS")
    print("=" * 70)
    
    # Get all collections
    collections = client.list_collections()
    
    if not collections:
        print("\n[INFO] No collections found in ChromaDB")
        return
    
    print(f"\nFound {len(collections)} collections:\n")
    
    collection_info = []
    
    for col in collections:
        count = col.count()
        
        # Determine status
        if col.name == "sebi_documents_advanced":
            status = "[KEEP] Corrected - 4,047 chunks with proper embeddings"
        elif col.name == "amlsim_transactions":
            status = "[KEEP] Correct - 10,401 documents with proper embeddings"
        elif col.name == "transactions_advanced":
            if count == 0:
                status = "[KEEP] Empty - may be used later"
            else:
                status = "[KEEP] Has data"
        elif col.name == "sebi_documents":
            status = "[DELETE] Old baseline - incorrect chunking/embeddings"
        elif col.name == "transactions":
            if count == 0:
                status = "[DELETE] Old baseline - empty"
            else:
                status = "[DELETE] Old baseline - may have incorrect embeddings"
        else:
            status = "[REVIEW] Unknown collection"
        
        collection_info.append({
            'name': col.name,
            'count': count,
            'status': status
        })
        
        print(f"Collection: {col.name}")
        print(f"  Documents: {count:,}")
        print(f"  Status: {status}")
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    to_delete = [c for c in collection_info if "[DELETE]" in c['status']]
    to_keep = [c for c in collection_info if "[KEEP]" in c['status']]
    
    if to_delete:
        print(f"\n[WARNING] Collections to DELETE ({len(to_delete)}):")
        for c in to_delete:
            print(f"  - {c['name']} ({c['count']:,} documents)")
            print(f"    Reason: Old baseline with incorrect embeddings/chunking")
    
    if to_keep:
        print(f"\n[OK] Collections to KEEP ({len(to_keep)}):")
        for c in to_keep:
            print(f"  - {c['name']} ({c['count']:,} documents)")
    
    print("\n" + "=" * 70)
    
    return to_delete, to_keep


def delete_collections(collections_to_delete):
    """Delete specified collections."""
    
    if not collections_to_delete:
        print("\n[INFO] No collections to delete")
        return
    
    chroma_path = Path("data/chroma_db")
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=ChromaSettings(anonymized_telemetry=False)
    )
    
    print("\n" + "=" * 70)
    print("DELETING OLD COLLECTIONS")
    print("=" * 70)
    
    for col_info in collections_to_delete:
        col_name = col_info['name']
        doc_count = col_info['count']
        
        print(f"\nDeleting: {col_name} ({doc_count:,} documents)...")
        
        try:
            client.delete_collection(name=col_name)
            print(f"  [OK] Successfully deleted '{col_name}'")
        except Exception as e:
            print(f"  [ERROR] Error deleting '{col_name}': {e}")
    
    print("\n" + "=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)


def main(delete_mode=False):
    """Main function to analyze and optionally delete collections."""
    
    to_delete, to_keep = analyze_collections()
    
    if not to_delete:
        print("\n[OK] No collections need to be deleted. Everything looks good!")
        return
    
    if delete_mode:
        print("\n[WARNING] DELETE MODE: Will delete the collections listed above")
        response = input("Continue? (yes/no): ")
        if response.lower() == 'yes':
            delete_collections(to_delete)
        else:
            print("\n[INFO] Deletion cancelled")
    else:
        print("\n[INFO] To delete these collections, run:")
        print("   python scripts/cleanup_old_chromadb_collections.py --delete")


if __name__ == "__main__":
    import sys
    
    delete_mode = "--delete" in sys.argv or "-d" in sys.argv
    
    main(delete_mode=delete_mode)

