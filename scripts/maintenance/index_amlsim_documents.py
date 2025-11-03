"""
Index AMLSim Transaction Documents in ChromaDB
Enables RAG queries on transaction data
Phase 4: Week 3-4 - AMLSim Integration
"""
import sys
from pathlib import Path
import time

# Add project root to path (go up 2 levels from scripts/maintenance/)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.amlsim_loader import AMLSimLoader
from src.data.amlsim_document_generator import AMLSimDocumentGenerator
from src.core.advanced_rag_engine import AdvancedRAGEngine

print("=" * 70)
print("AMLSim Transaction Document Indexing")
print("Phase 4 - Week 3-4")
print("=" * 70)

# Step 1: Load AMLSim data
print("\n[Step 1] Loading AMLSim data...")
try:
    loader = AMLSimLoader()
    data = loader.load_all_data()
    
    accounts_df = data['accounts']
    transactions_df = data['transactions']
    alerts_df = data['alerts']
    
    if accounts_df.empty or transactions_df.empty:
        print("  [FAIL] No AMLSim data found!")
        print("  Run: python generate_amlsim_compatible_data.py")
        sys.exit(1)
    
    print(f"  [OK] Loaded:")
    print(f"    - Accounts: {len(accounts_df):,}")
    print(f"    - Transactions: {len(transactions_df):,}")
    print(f"    - Alerts: {len(alerts_df):,}")
    
except Exception as e:
    print(f"  [FAIL] Loading failed: {e}")
    sys.exit(1)

# Step 2: Generate transaction documents
print("\n[Step 2] Generating natural language documents...")
print("  This may take a few minutes...")

start_time = time.time()

try:
    doc_generator = AMLSimDocumentGenerator()
    
    documents = doc_generator.batch_generate_documents(
        transactions_df=transactions_df,
        accounts_df=accounts_df,
        alerts_df=alerts_df
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"  [OK] Generated {len(documents):,} documents in {elapsed_time:.2f}s")
    print(f"  Rate: {len(documents)/elapsed_time:.0f} documents/second")
    
    # Show sample
    if documents:
        sample = documents[0]
        print(f"\n  Sample Document (first 500 chars):")
        print(f"  {sample['document'][:500]}...")
    
except Exception as e:
    print(f"  [FAIL] Document generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Initialize RAG engine
print("\n[Step 3] Initializing RAG engine...")
try:
    rag_engine = AdvancedRAGEngine(
        persist_directory="./data/chroma_db",
        ollama_model="llama3.1:8b"
    )
    print("  [OK] RAG engine initialized")
    
except Exception as e:
    print(f"  [FAIL] RAG engine initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Index documents in ChromaDB
print("\n[Step 4] Indexing documents in ChromaDB...")
print("  Creating embeddings and indexing...")

try:
    # Check if collection exists
    try:
        # Get or create AMLSim collection
        amlsim_collection = rag_engine.chroma_client.get_or_create_collection(
            name="amlsim_transactions",
            metadata={"description": "AMLSim transaction data with fraud patterns"}
        )
        print(f"  [OK] Collection ready: amlsim_transactions")
    except Exception as e:
        print(f"  [WARNING] Collection issue: {e}")
        amlsim_collection = rag_engine.chroma_client.create_collection(
            name="amlsim_transactions"
        )
    
    # Prepare documents for indexing
    doc_texts = [d['document'] for d in documents]
    doc_ids = [d['doc_id'] for d in documents]
    
    # Filter out None values from metadata (ChromaDB doesn't accept None)
    doc_metadatas = []
    for d in documents:
        metadata = {k: v for k, v in d['metadata'].items() if v is not None}
        # Convert all values to strings/numbers (ChromaDB requirement)
        clean_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, (int, float, str, bool)):
                clean_metadata[key] = value
            else:
                clean_metadata[key] = str(value)
        doc_metadatas.append(clean_metadata)
    
    # Generate embeddings (in batches for efficiency)
    batch_size = 500
    total_indexed = 0
    
    for i in range(0, len(doc_texts), batch_size):
        batch_docs = doc_texts[i:i+batch_size]
        batch_ids = doc_ids[i:i+batch_size]
        batch_metas = doc_metadatas[i:i+batch_size]
        
        # Generate embeddings
        embeddings = rag_engine.embedding_model.encode(batch_docs).tolist()
        
        # Add to collection
        amlsim_collection.add(
            documents=batch_docs,
            embeddings=embeddings,
            metadatas=batch_metas,
            ids=batch_ids
        )
        
        total_indexed += len(batch_docs)
        print(f"  Progress: {total_indexed:,}/{len(doc_texts):,} documents indexed")
    
    print(f"  [OK] Indexed {total_indexed:,} documents in ChromaDB")
    
except Exception as e:
    print(f"  [FAIL] Indexing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test RAG queries
print("\n[Step 5] Testing RAG queries on AMLSim data...")

test_queries = [
    "Show me transactions with fan-out patterns",
    "Which accounts have large outgoing transfers?",
    "Find suspicious activity alerts",
    "What are the money laundering patterns?",
    "Show me high-risk transactions"
]

print("\n  Running test queries...")
for query in test_queries[:3]:  # Test first 3
    print(f"\n  Query: '{query}'")
    
    try:
        # Query the AMLSim collection
        query_embedding = rag_engine.embedding_model.encode([query]).tolist()[0]
        
        results = amlsim_collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        if results['documents'] and results['documents'][0]:
            print(f"    [OK] Found {len(results['documents'][0])} results")
            print(f"    Top result: {results['documents'][0][0][:200]}...")
        else:
            print(f"    [WARNING] No results found")
    
    except Exception as e:
        print(f"    [FAIL] Query failed: {e}")

print("\n  [OK] RAG query testing complete")

# Summary
print("\n" + "=" * 70)
print("AMLSim Document Indexing Complete!")
print("=" * 70)

print(f"\nIndexing Summary:")
print(f"  Documents generated: {len(documents):,}")
print(f"  Documents indexed: {total_indexed:,}")
print(f"  Collection: amlsim_transactions")
print(f"  Processing time: {elapsed_time:.2f}s")

print(f"\nChromaDB Collections:")
print(f"  - sebi_documents_advanced (SEBI regulatory docs)")
print(f"  - amlsim_transactions (Transaction data) [NEW!]")

print(f"\nNow you can query:")
print(f'  - "Find transactions similar to SEBI money laundering cases"')
print(f'  - "Show me all fan-out pattern transactions"')
print(f'  - "Which accounts are involved in suspicious activity?"')

print("\nNext: Unified GraphRAG system (Week 5-6)")
print("=" * 70)

