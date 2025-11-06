"""
Rebuild SEBI ChromaDB with Corrected Document Classifications

This script:
1. Deletes the existing SEBI collection
2. Re-indexes ALL SEBI documents with correct document_type classification
3. Uses the improved sebi_file_processor.py classification logic

Use this script when:
- Adding new SEBI documents
- Fixing classification issues
- Updating the ChromaDB schema
"""

import chromadb
from pathlib import Path
from src.data.sebi_processor import SEBIProcessor
from src.data.sebi_file_processor import SEBIFileProcessor
from datetime import datetime
from sentence_transformers import SentenceTransformer
from src.core.device_config import get_device_string

def rebuild_sebi_chromadb():
    """Rebuild SEBI ChromaDB from scratch with correct classifications and embeddings"""
    
    print("\n" + "="*70)
    print("REBUILDING SEBI CHROMADB WITH CORRECTED CHUNKING & EMBEDDINGS")
    print("="*70)
    
    # Initialize ChromaDB client
    chroma_path = Path("data/chroma_db")
    client = chromadb.PersistentClient(path=str(chroma_path))
    
    # Step 1: Delete existing SEBI collection (ADVANCED version used by unified engine)
    print("\n[1/5] Deleting existing SEBI collection...")
    try:
        client.delete_collection(name="sebi_documents_advanced")
        print("[OK] Deleted old 'sebi_documents_advanced' collection")
    except Exception as e:
        print(f"  Note: {e} (collection may not exist)")
    
    # Step 2: Create fresh collection (with ADVANCED suffix)
    print("\n[2/5] Creating fresh SEBI collection...")
    collection = client.get_or_create_collection(
        name="sebi_documents_advanced",
        metadata={"hnsw:space": "cosine", "description": "SEBI documents with advanced features"}
    )
    print("[OK] Created new 'sebi_documents_advanced' collection")
    
    # Step 3: Initialize processors and embedding model
    print("\n[3/5] Initializing processors and embedding model...")
    sebi_processor = SEBIProcessor()
    file_processor = SEBIFileProcessor()
    
    # Initialize fine-tuned embedding model (same as used in RAG engine)
    device = get_device_string()
    print(f"  Using device: {device}")
    embedding_model = SentenceTransformer('models/fin-e5', device=device)
    print(f"  Loaded fine-tuned embedding model: Fin-E5 (768 dimensions)")
    print(f"  Model trained on SEBI/AMLSim domain data")
    print("[OK] Processors and embedding model initialized")
    
    # Step 4: Process ALL SEBI documents
    print("\n[4/5] Processing and chunking ALL SEBI documents...")
    
    # Find all SEBI PDF files in both directories
    sebi_dir = Path("data/sebi")
    additional_dir = Path("data/additional_sebi")
    
    all_pdf_files = []
    
    if sebi_dir.exists():
        pdf_files = list(sebi_dir.glob("*.pdf"))
        all_pdf_files.extend(pdf_files)
        print(f"  Found {len(pdf_files)} PDFs in data/sebi/")
    
    if additional_dir.exists():
        pdf_files = list(additional_dir.glob("*.pdf"))
        all_pdf_files.extend(pdf_files)
        print(f"  Found {len(pdf_files)} PDFs in data/additional_sebi/")
    
    print(f"\n  Total PDFs to process: {len(all_pdf_files)}")
    
    if not all_pdf_files:
        print("\n[ERROR] No PDF files found!")
        return
    
    # Track statistics
    stats = {
        'regulation': 0,
        'adjudication_order': 0,
        'investigation_report': 0,
        'press_release': 0,
        'circular': 0,
        'other': 0,
        'total_chunks': 0,
        'errors': 0
    }
    
    # Batch accumulator for efficient embedding generation
    batch_documents = []
    batch_metadatas = []
    batch_ids = []
    batch_size = 100  # Process 100 chunks at a time
    
    # Process each PDF
    for i, pdf_path in enumerate(all_pdf_files, 1):
        try:
            print(f"\n  [{i}/{len(all_pdf_files)}] Processing: {pdf_path.name[:50]}...")
            
            # Process file using SEBIFileProcessor (handles extraction, type detection, etc.)
            doc = file_processor.process_file(pdf_path)
            
            if not doc or not doc.content or len(doc.content.strip()) < 100:
                print(f"    [WARN] Skipped (insufficient content)")
                stats['errors'] += 1
                continue
            
            # Get document type from processed document
            doc_type = doc.document_type
            stats[doc_type] = stats.get(doc_type, 0) + 1
            
            # Convert document to dict for processing
            doc_dict = {
                'document_id': doc.document_id,
                'title': doc.title,
                'document_type': doc.document_type,
                'url': doc.file_path,
                'date': doc.date.isoformat() if doc.date else None,
                'content': doc.content,
                'metadata': doc.metadata
            }
            
            # Create chunks using SEBI processor
            chunks = sebi_processor.process_documents([doc_dict])
            
            if not chunks:
                print(f"    [WARN] No chunks generated")
                stats['errors'] += 1
                continue
            
            # Prepare chunks for batching
            for chunk in chunks:
                # Prepare metadata (ensure ChromaDB compatible types)
                metadata = {
                    'source': str(pdf_path),
                    'chunk_index': chunk.chunk_index,
                    'total_chunks': len(chunks),
                    'document_type': doc_type,
                    'title': doc.title
                }
                
                # Add date if available
                if doc.date:
                    metadata['date'] = doc.date.isoformat() if hasattr(doc.date, 'isoformat') else str(doc.date)
                
                # Ensure all metadata values are compatible types (no None)
                clean_metadata = {}
                for key, value in metadata.items():
                    if value is not None:
                        if isinstance(value, (str, int, float, bool)):
                            clean_metadata[key] = value
                        else:
                            clean_metadata[key] = str(value)
                
                # Add to batch
                batch_documents.append(chunk.content)
                batch_metadatas.append(clean_metadata)
                batch_ids.append(chunk.chunk_id)
            
            stats['total_chunks'] += len(chunks)
            
            # Show doc type with marker
            marker = "[REG]" if doc_type == 'regulation' else "[CASE]"
            print(f"    [OK] {marker} Type: {doc_type}, Chunks: {len(chunks)}")
            
            # Process batch if it reaches batch_size
            if len(batch_documents) >= batch_size:
                print(f"  [BATCH] Generating embeddings for {len(batch_documents)} chunks...")
                embeddings = embedding_model.encode(batch_documents, show_progress_bar=False).tolist()
                
                collection.add(
                    documents=batch_documents,
                    embeddings=embeddings,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                print(f"  [BATCH] Indexed {len(batch_documents)} chunks to ChromaDB")
                
                # Clear batch
                batch_documents = []
                batch_metadatas = []
                batch_ids = []
        
        except Exception as e:
            print(f"    [ERROR] {str(e)[:100]}")
            stats['errors'] += 1
            continue
    
    # Step 5: Process any remaining documents in the batch
    print("\n[5/5] Processing final batch...")
    if batch_documents:
        print(f"  Generating embeddings for {len(batch_documents)} remaining chunks...")
        embeddings = embedding_model.encode(batch_documents, show_progress_bar=False).tolist()
        
        collection.add(
            documents=batch_documents,
            embeddings=embeddings,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        print(f"  [OK] Indexed final {len(batch_documents)} chunks to ChromaDB")
    
    # Final statistics
    print("\n" + "="*70)
    print("REBUILD COMPLETE - IMPROVED CHUNKING & EMBEDDINGS")
    print("="*70)
    print(f"\nDocument Type Distribution:")
    print(f"  Regulations:          {stats.get('regulation', 0):>3}")
    print(f"  Adjudication Orders:  {stats.get('adjudication_order', 0):>3}")
    print(f"  Investigation Reports:{stats.get('investigation_report', 0):>3}")
    print(f"  Press Releases:       {stats.get('press_release', 0):>3}")
    print(f"  Circulars:            {stats.get('circular', 0):>3}")
    print(f"  Other:                {stats.get('other', 0):>3}")
    print(f"\nTotal Chunks: {stats['total_chunks']}")
    print(f"Errors: {stats['errors']}")
    print(f"\nImprovements Applied:")
    print(f"  [OK] Token-based chunking with {sebi_processor.chunk_overlap}-token overlap")
    print(f"  [OK] Sentence boundary preservation")
    print(f"  [OK] Explicit embedding generation using all-MiniLM-L12-v2")
    print(f"  [OK] Batch processing for efficiency")
    print("="*70)

if __name__ == "__main__":
    rebuild_sebi_chromadb()

