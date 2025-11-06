"""
Embed FIU and Income Tax Data into ChromaDB

This script follows the updated pipeline pattern:
1. Processes files one by one (not all at once)
2. For each file: process → chunk → add to batch accumulator
3. When batch reaches size, generate embeddings and store
4. Uses the same metadata structure as rebuild_sebi_chromadb.py

Usage:
    python embed_fiu_incometax_data.py
"""

import chromadb
from pathlib import Path
from src.data.text_file_processor import TextFileProcessor
from src.data.sebi_processor import SEBIProcessor
from src.core.config import settings
from sentence_transformers import SentenceTransformer
from src.core.device_config import get_device_string
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def embed_fiu_incometax_data():
    """Process and embed FIU and Income Tax documents into ChromaDB following updated pipeline"""
    
    print("\n" + "="*70)
    print("EMBEDDING FIU AND INCOME TAX DATA INTO CHROMADB")
    print("Following Updated Pipeline: File-by-File Processing with Batch Accumulation")
    print("="*70)
    
    # Initialize ChromaDB client
    chroma_path = Path(settings.chroma_persist_directory)
    client = chromadb.PersistentClient(path=str(chroma_path))
    
    # Step 1: Create or get collections
    print("\n[1/5] Setting up ChromaDB collections...")
    fiu_collection = client.get_or_create_collection(
        name="fiu_documents_advanced",
        metadata={"hnsw:space": "cosine", "description": "FIU documents with advanced features"}
    )
    incometax_collection = client.get_or_create_collection(
        name="incometax_documents_advanced",
        metadata={"hnsw:space": "cosine", "description": "Income Tax documents with advanced features"}
    )
    print("[OK] Collections ready")
    
    # Step 2: Initialize processors and embedding model
    print("\n[2/5] Initializing processors and embedding model...")
    text_processor = TextFileProcessor()
    sebi_processor = SEBIProcessor()  # Use default settings (matches rebuild_sebi_chromadb.py)
    
    # Initialize fine-tuned embedding model (same as rebuild_sebi_chromadb.py)
    device = get_device_string()
    print(f"  Using device: {device}")
    embedding_model = SentenceTransformer(settings.embedding_model, device=device)
    print(f"  Loaded embedding model: Fin-E5 (768 dimensions)")
    print(f"  Model path: {settings.embedding_model}")
    print("[OK] Processors and embedding model initialized")
    
    # Step 3: Process FIU documents (file-by-file with batch accumulation)
    print("\n[3/5] Processing FIU documents...")
    fiu_dir = Path(settings.fiu_data_path)
    
    if not fiu_dir.exists():
        print(f"  [WARNING] FIU directory not found: {fiu_dir}")
        fiu_stats = {'total_chunks': 0, 'errors': 0}
    else:
        fiu_stats = _process_documents_file_by_file(
            directory=fiu_dir,
            text_processor=text_processor,
            sebi_processor=sebi_processor,
            embedding_model=embedding_model,
            collection=fiu_collection,
            source_name="FIU"
        )
    
    # Step 4: Process Income Tax documents (file-by-file with batch accumulation)
    print("\n[4/5] Processing Income Tax documents...")
    incometax_dir = Path(settings.incometax_data_path)
    
    if not incometax_dir.exists():
        print(f"  [WARNING] Income Tax directory not found: {incometax_dir}")
        incometax_stats = {'total_chunks': 0, 'errors': 0}
    else:
        incometax_stats = _process_documents_file_by_file(
            directory=incometax_dir,
            text_processor=text_processor,
            sebi_processor=sebi_processor,
            embedding_model=embedding_model,
            collection=incometax_collection,
            source_name="Income Tax"
        )
    
    # Step 5: Summary
    print("\n[5/5] Summary...")
    print("="*70)
    print("EMBEDDING COMPLETE - UPDATED PIPELINE")
    print("="*70)
    print(f"\nFIU Collection:")
    print(f"  Total Chunks: {fiu_stats['total_chunks']}")
    print(f"  Errors: {fiu_stats['errors']}")
    print(f"  Collection Count: {fiu_collection.count()}")
    print(f"\nIncome Tax Collection:")
    print(f"  Total Chunks: {incometax_stats['total_chunks']}")
    print(f"  Errors: {incometax_stats['errors']}")
    print(f"  Collection Count: {incometax_collection.count()}")
    print(f"\nPipeline Features Applied:")
    print(f"  [OK] File-by-file processing")
    print(f"  [OK] Batch accumulation (100 chunks per batch)")
    print(f"  [OK] Token-based chunking with {sebi_processor.chunk_overlap}-token overlap")
    print(f"  [OK] Sentence boundary preservation")
    print(f"  [OK] Explicit embedding generation using Fin-E5")
    print("="*70)


def _process_documents_file_by_file(directory, text_processor, sebi_processor, 
                                   embedding_model, collection, source_name, batch_size=100):
    """
    Process documents file-by-file following the updated pipeline pattern.
    Matches the approach used in rebuild_sebi_chromadb.py.
    
    Args:
        directory: Directory containing text files
        text_processor: TextFileProcessor instance
        sebi_processor: SEBIProcessor instance
        embedding_model: SentenceTransformer model
        collection: ChromaDB collection
        source_name: Name of source for logging
        batch_size: Batch size for embedding generation
        
    Returns:
        Dictionary with processing statistics
    """
    # Find all text files
    txt_files = list(directory.glob("*.txt"))
    print(f"  Found {len(txt_files)} text files in {directory}")
    
    if not txt_files:
        print("  [WARNING] No text files found!")
        return {'total_chunks': 0, 'errors': 0}
    
    # Track statistics
    stats = {
        'total_chunks': 0,
        'errors': 0
    }
    
    # Batch accumulator for efficient embedding generation
    batch_documents = []
    batch_metadatas = []
    batch_ids = []
    
    # Process each file one by one
    for i, txt_file in enumerate(txt_files, 1):
        try:
            print(f"\n  [{i}/{len(txt_files)}] Processing: {txt_file.name[:50]}...")
            
            # Process file using TextFileProcessor
            doc = text_processor.process_file(txt_file)
            
            if not doc or not doc.content or len(doc.content.strip()) < 100:
                print(f"    [WARN] Skipped (insufficient content)")
                stats['errors'] += 1
                continue
            
            # Get document type from processed document
            doc_type = doc.document_type
            
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
            
            # Create chunks using SEBI processor (processes single document)
            chunks = sebi_processor.process_documents([doc_dict])
            
            if not chunks:
                print(f"    [WARN] No chunks generated")
                stats['errors'] += 1
                continue
            
            # Prepare chunks for batching (matching rebuild_sebi_chromadb.py metadata structure)
            for chunk in chunks:
                # Prepare metadata (ensure ChromaDB compatible types)
                # Match the structure from rebuild_sebi_chromadb.py
                metadata = {
                    'source': str(txt_file),
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
            print(f"    [OK] Type: {doc_type}, Chunks: {len(chunks)}")
            
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
    
    # Process any remaining documents in the batch
    if batch_documents:
        print(f"\n  [BATCH] Generating embeddings for {len(batch_documents)} remaining chunks...")
        embeddings = embedding_model.encode(batch_documents, show_progress_bar=False).tolist()
        
        collection.add(
            documents=batch_documents,
            embeddings=embeddings,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        print(f"  [BATCH] Indexed final {len(batch_documents)} chunks to ChromaDB")
    
    return stats


if __name__ == "__main__":
    embed_fiu_incometax_data()

