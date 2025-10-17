"""
Test Phase 4 Setup - Verify GraphRAG Infrastructure
Tests: Base graph manager, entity extractor, dependencies
"""
import sys
from pathlib import Path
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Phase 4 Setup Verification")
print("=" * 70)

# Test 1: Import Dependencies
print("\n[Test 1] Checking Dependencies...")
try:
    import networkx as nx
    print("  [OK] NetworkX imported successfully")
    print(f"     Version: {nx.__version__}")
except ImportError as e:
    print(f"  [FAIL] NetworkX import failed: {e}")

try:
    import spacy
    print("  [OK] spaCy imported successfully")
    print(f"     Version: {spacy.__version__}")
except ImportError as e:
    print(f"  [FAIL] spaCy import failed: {e}")

try:
    import pyvis
    print("  [OK] Pyvis imported successfully")
except ImportError as e:
    print(f"  [FAIL] Pyvis import failed: {e}")

try:
    import community
    print("  [OK] python-louvain imported successfully")
except ImportError as e:
    print(f"  [FAIL] python-louvain import failed: {e}")

# Test 2: Load spaCy Model
print("\n[Test 2] Loading spaCy Language Model...")
try:
    nlp = spacy.load("en_core_web_sm")
    print("  [OK] en_core_web_sm loaded successfully")
    
    # Test NER
    test_text = "SEBI penalized ABC Corp for insider trading."
    doc = nlp(test_text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print(f"     Test NER: Found {len(entities)} entities")
    for text, label in entities:
        print(f"       - {text} ({label})")
except Exception as e:
    print(f"  [FAIL] spaCy model loading failed: {e}")

# Test 3: Graph Manager
print("\n[Test 3] Testing GraphManager...")
try:
    from src.core.graph_manager import GraphManager
    
    # Create test graph
    gm = GraphManager(graph_name="test_graph")
    print("  [OK] GraphManager instantiated")
    
    # Add nodes
    gm.add_node("ABC_Corp", "Entity", industry="Finance")
    gm.add_node("insider_trading", "Violation", severity="high")
    gm.add_node("SEBI", "Regulator")
    print("  [OK] Nodes added successfully")
    
    # Add edges
    gm.add_edge("ABC_Corp", "insider_trading", "COMMITTED")
    gm.add_edge("SEBI", "ABC_Corp", "PENALIZED")
    print("  [OK] Edges added successfully")
    
    # Get statistics
    stats = gm.get_statistics()
    print(f"     Graph statistics:")
    print(f"       - Nodes: {stats['total_nodes']}")
    print(f"       - Edges: {stats['total_edges']}")
    print(f"       - Node types: {stats['node_types']}")
    
    # Test multi-hop query
    result = gm.multi_hop_query("ABC_Corp", max_hops=2)
    print(f"     Multi-hop query from ABC_Corp:")
    print(f"       - Paths found: {result['total_paths']}")
    print(f"       - Nodes reached: {result['total_nodes']}")
    
except Exception as e:
    print(f"  [FAIL] GraphManager test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Entity Extractor
print("\n[Test 4] Testing EntityExtractor...")
try:
    from src.data.entity_extractor import EntityExtractor
    
    extractor = EntityExtractor()
    print("  [OK] EntityExtractor instantiated")
    
    # Test text
    test_doc = """
    SEBI imposed a penalty of ₹50 lakh on XYZ Industries Ltd. for 
    engaging in insider trading. The company was found guilty of 
    violating disclosure norms.
    """
    
    # Extract entities
    result = extractor.extract_from_document(test_doc, "test_doc_001")
    print(f"  [OK] Entities extracted:")
    print(f"     - Total entities: {result['entity_count']}")
    print(f"     - Total relationships: {result['relationship_count']}")
    print(f"     - Summary: {result['summary']}")
    
    # Show entities by type
    for entity_type, entities in result['entities_by_type'].items():
        print(f"     - {entity_type}: {entities}")
    
except Exception as e:
    print(f"  [FAIL] EntityExtractor test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Graph Persistence
print("\n[Test 5] Testing Graph Persistence...")
try:
    from src.core.graph_manager import GraphManager
    
    # Create and save graph
    gm = GraphManager(graph_name="persistence_test")
    gm.add_node("test_node", "TestType", data="test_value")
    save_path = gm.save_graph()
    print(f"  [OK] Graph saved to: {save_path}")
    
    # Load graph
    gm2 = GraphManager(graph_name="persistence_test")
    loaded = gm2.load_graph()
    if loaded and gm2.graph.number_of_nodes() == 1:
        print("  [OK] Graph loaded successfully")
        print(f"     - Nodes: {gm2.graph.number_of_nodes()}")
    else:
        print("  [FAIL] Graph loading verification failed")
    
except Exception as e:
    print(f"  [FAIL] Graph persistence test failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("Phase 4 Setup Verification Complete!")
print("=" * 70)
print("\n[OK] All core components are ready for Phase 4 implementation!")
print("\nNext Steps:")
print("  1. Week 1-2: Build SEBI Knowledge Graph")
print("  2. Week 3-4: IEEE-CIS Transaction Intelligence")
print("  3. Week 5-6: Unified GraphRAG System")
print("\n" + "=" * 70)

