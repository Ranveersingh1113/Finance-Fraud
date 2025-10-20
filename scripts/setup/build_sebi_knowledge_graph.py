"""
Build SEBI Knowledge Graph from processed documents.
Phase 4 - Week 1-2: SEBI Knowledge Graph Construction
"""
import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.sebi_graph_manager import SEBIGraphManager
from src.data.ingestion import DataIngestion

print("=" * 70)
print("SEBI Knowledge Graph Construction")
print("Phase 4 - Week 1-2")
print("=" * 70)

# Initialize components
print("\n[Step 1] Initializing components...")
try:
    data_ingestion = DataIngestion()
    graph_manager = SEBIGraphManager()
    print("  [OK] Components initialized")
except Exception as e:
    print(f"  [FAIL] Initialization failed: {e}")
    sys.exit(1)

# Load processed SEBI chunks
print("\n[Step 2] Loading processed SEBI documents...")
try:
    sebi_chunks = data_ingestion.load_processed_sebi_chunks()
    
    if not sebi_chunks:
        print("  [WARNING] No SEBI chunks found!")
        print("  Please run: python test_complete_sebi_pipeline.py")
        sys.exit(1)
    
    print(f"  [OK] Loaded {len(sebi_chunks)} SEBI document chunks")
    
    # Show sample
    if sebi_chunks:
        sample = sebi_chunks[0]
        print(f"  Sample: {sample.title[:50]}...")
        print(f"  Document type: {sample.document_type}")
        print(f"  Violations: {sample.violation_types[:3]}")
        
except Exception as e:
    print(f"  [FAIL] Loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Build knowledge graph
print(f"\n[Step 3] Building knowledge graph from {len(sebi_chunks)} documents...")
print("  This may take a few minutes...")

start_time = time.time()

try:
    # Process in batch
    result = graph_manager.process_sebi_documents_batch(sebi_chunks)
    
    elapsed_time = time.time() - start_time
    
    print(f"\n  [OK] Knowledge graph built in {elapsed_time:.2f} seconds")
    print(f"  Documents processed: {result['documents_processed']}")
    print(f"  Entities added: {result['total_entities']}")
    print(f"  Relationships added: {result['total_relationships']}")
    
    if result['errors'] > 0:
        print(f"  [WARNING] Errors encountered: {result['errors']}")
    
except Exception as e:
    print(f"  [FAIL] Graph building failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Get graph statistics
print("\n[Step 4] Analyzing knowledge graph...")
try:
    stats = graph_manager.get_sebi_statistics()
    
    print("\n  Graph Statistics:")
    print(f"  Total Nodes: {stats['total_nodes']}")
    print(f"  Total Edges: {stats['total_edges']}")
    
    print("\n  Node Types:")
    for node_type, count in stats['node_types'].items():
        print(f"    - {node_type}: {count}")
    
    print("\n  Relationship Types:")
    for rel_type, count in stats['relationship_types'].items():
        print(f"    - {rel_type}: {count}")
    
    sebi_stats = stats['sebi_specific']
    print(f"\n  SEBI-Specific Metrics:")
    print(f"    - Entities: {sebi_stats['entities']}")
    print(f"    - Violations: {sebi_stats['violations']}")
    print(f"    - Documents: {sebi_stats['documents']}")
    print(f"    - Regulators: {sebi_stats['regulators']}")
    print(f"    - Penalties: {sebi_stats['penalties']}")
    
    print("\n  Top 5 Most Cited Entities:")
    for i, entity in enumerate(stats['top_entities'][:5], 1):
        print(f"    {i}. {entity['name']} ({entity['citations']} citations)")
    
    print("\n  Top 5 Most Common Violations:")
    for i, violation in enumerate(stats['top_violations'][:5], 1):
        print(f"    {i}. {violation['name']} ({violation['citations']} occurrences)")
    
except Exception as e:
    print(f"  [FAIL] Statistics generation failed: {e}")

# Save graph
print("\n[Step 5] Saving knowledge graph...")
try:
    # Save as pickle
    save_path = graph_manager.save_graph()
    print(f"  [OK] Graph saved to: {save_path}")
    
    # Export for visualization
    viz_path = graph_manager.export_for_visualization()
    print(f"  [OK] Visualization data exported to: {viz_path}")
    
    # Export as JSON
    json_path = graph_manager.export_to_json()
    print(f"  [OK] JSON export saved to: {json_path}")
    
except Exception as e:
    print(f"  [FAIL] Saving failed: {e}")

# Test queries
print("\n[Step 6] Testing knowledge graph queries...")

try:
    # Test 1: Find violations for an entity (if any entities exist)
    if stats['sebi_specific']['entities'] > 0:
        test_entity = stats['top_entities'][0]['name'] if stats['top_entities'] else None
        
        if test_entity:
            print(f"\n  Query 1: Violations by '{test_entity}'")
            violations = graph_manager.find_entity_violations(test_entity)
            if violations:
                for v in violations[:3]:
                    print(f"    - {v['violation']} (confidence: {v['confidence']:.2f})")
            else:
                print("    No violations found")
    
    # Test 2: Find similar cases
    if stats['sebi_specific']['violations'] > 0:
        test_violation = stats['top_violations'][0]['name'] if stats['top_violations'] else None
        
        if test_violation:
            print(f"\n  Query 2: Cases similar to '{test_violation}'")
            similar = graph_manager.find_similar_cases(test_violation, limit=3)
            if similar:
                for case in similar:
                    print(f"    - {case['entity']} ({case['citation_count']} citations)")
            else:
                print("    No similar cases found")
    
    # Test 3: Multi-hop traversal
    if stats['total_nodes'] > 0:
        # Get a random entity node
        entity_nodes = graph_manager.find_nodes_by_type('Entity')
        if entity_nodes:
            test_node = entity_nodes[0]
            print(f"\n  Query 3: Multi-hop traversal from node")
            result = graph_manager.multi_hop_query(test_node, max_hops=2)
            print(f"    - Paths found: {result['total_paths']}")
            print(f"    - Nodes reached: {result['total_nodes']}")
            print(f"    - Relationships: {len(result['relationships'])}")
    
    print("\n  [OK] All test queries completed successfully")
    
except Exception as e:
    print(f"  [FAIL] Query testing failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("SEBI Knowledge Graph Construction Complete!")
print("=" * 70)

print("\n[OK] Week 1-2 Milestone Achieved!")
print("\nGraph Summary:")
print(f"  - {stats['total_nodes']} nodes")
print(f"  - {stats['total_edges']} edges")
print(f"  - {sebi_stats['entities']} entities")
print(f"  - {sebi_stats['violations']} violation types")
print(f"  - {sebi_stats['documents']} documents indexed")

print("\nSaved Files:")
print(f"  - Graph: {save_path}")
print(f"  - Visualization: {viz_path}")
print(f"  - JSON: {json_path}")

print("\nNext Steps:")
print("  1. Test SEBI graph queries")
print("  2. Week 3-4: IEEE-CIS Transaction Intelligence")
print("  3. Week 5-6: Unified GraphRAG System")

print("\n" + "=" * 70)

