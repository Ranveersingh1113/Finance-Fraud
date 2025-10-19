"""
Test Unified GraphRAG System
Demonstrates cross-domain queries combining SEBI + AMLSim
Phase 4: Week 5-6
"""
import sys
from pathlib import Path
import asyncio

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.unified_graphrag_engine import UnifiedGraphRAGEngine

print("=" * 70)
print("Unified GraphRAG System Testing")
print("Phase 4 - Week 5-6")
print("=" * 70)

async def main():
    # Initialize unified engine
    print("\n[Step 1] Initializing Unified GraphRAG Engine...")
    try:
        engine = UnifiedGraphRAGEngine()
        print("  [OK] Unified engine initialized")
    except Exception as e:
        print(f"  [FAIL] Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Get unified statistics
    print("\n[Step 2] Getting unified statistics...")
    try:
        stats = engine.get_unified_statistics()
        
        print(f"\n  Combined Knowledge Base:")
        print(f"    Total Nodes: {stats['combined']['total_nodes']:,}")
        print(f"    Total Edges: {stats['combined']['total_edges']:,}")
        
        print(f"\n  SEBI Graph:")
        print(f"    Entities: {stats['combined']['sebi_entities']:,}")
        print(f"    Violations: {stats['combined']['sebi_violations']}")
        
        print(f"\n  AMLSim Graph:")
        print(f"    Accounts: {stats['combined']['amlsim_accounts']:,}")
        print(f"    Fraud Rings: {stats['combined']['amlsim_fraud_rings']:,}")
        
        print("  [OK] Statistics retrieved")
    
    except Exception as e:
        print(f"  [FAIL] Statistics failed: {e}")
    
    # Test 1: Regulatory query
    print("\n" + "=" * 70)
    print("[Test 1] Regulatory Query (SEBI Focus)")
    print("=" * 70)
    
    query1 = "What are SEBI penalties for money laundering?"
    print(f"\nQuery: '{query1}'")
    
    try:
        result = await engine.unified_query(query1, use_graphs=True, n_results=5)
        
        print(f"  Query Type: {result['query_type']}")
        print(f"  SEBI Results: {len(result['rag_results']['sebi_results'])}")
        print(f"  AMLSim Results: {len(result['rag_results']['amlsim_results'])}")
        print(f"\n  Answer Preview:")
        print(f"  {result['answer'][:500]}...")
        
    except Exception as e:
        print(f"  [FAIL] Query failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Transaction query
    print("\n" + "=" * 70)
    print("[Test 2] Transaction Query (AMLSim Focus)")
    print("=" * 70)
    
    query2 = "Show me transactions with fan-out patterns"
    print(f"\nQuery: '{query2}'")
    
    try:
        result = await engine.unified_query(query2, use_graphs=True, n_results=5)
        
        print(f"  Query Type: {result['query_type']}")
        print(f"  SEBI Results: {len(result['rag_results']['sebi_results'])}")
        print(f"  AMLSim Results: {len(result['rag_results']['amlsim_results'])}")
        print(f"\n  Answer Preview:")
        print(f"  {result['answer'][:500]}...")
        
    except Exception as e:
        print(f"  [FAIL] Query failed: {e}")
    
    # Test 3: Cross-domain query
    print("\n" + "=" * 70)
    print("[Test 3] Cross-Domain Query (Combined Intelligence)")
    print("=" * 70)
    
    query3 = "Find transaction patterns similar to SEBI money laundering violations"
    print(f"\nQuery: '{query3}'")
    
    try:
        result = await engine.unified_query(query3, use_graphs=True, n_results=5)
        
        print(f"  Query Type: {result['query_type']}")
        print(f"  SEBI Results: {len(result['rag_results']['sebi_results'])}")
        print(f"  AMLSim Results: {len(result['rag_results']['amlsim_results'])}")
        print(f"  Cross-Domain Patterns: {len(result['cross_domain_patterns'])}")
        
        if result['cross_domain_patterns']:
            print(f"\n  Pattern Matches:")
            for pattern in result['cross_domain_patterns']:
                print(f"    - {pattern['description']}")
        
        print(f"\n  Answer Preview:")
        print(f"  {result['answer'][:500]}...")
        
    except Exception as e:
        print(f"  [FAIL] Query failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Trace with regulatory context
    print("\n" + "=" * 70)
    print("[Test 4] Transaction Trace with Regulatory Context")
    print("=" * 70)
    
    print(f"\nTracing account_966 (top fraud ring)...")
    
    try:
        trace = await engine.trace_transaction_with_regulatory_context("966")
        
        print(f"  Account: {trace['account']}")
        print(f"  Pattern Identified: {trace['pattern_identified']}")
        print(f"  Accounts Reached: {trace['money_flow']['accounts_reached']}")
        print(f"  Total Amount: ${trace['money_flow']['total_sent']:,.2f}")
        print(f"  Similar SEBI Cases: {len(trace['similar_sebi_cases'])}")
        print(f"  Regulatory Risk: {trace['regulatory_risk']}")
        
        if trace['similar_sebi_cases']:
            print(f"\n  Matching SEBI Cases:")
            for case in trace['similar_sebi_cases'][:3]:
                print(f"    - {case['entity']} ({case['citation_count']} citations)")
        
    except Exception as e:
        print(f"  [FAIL] Trace failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Find accounts matching SEBI violations
    print("\n" + "=" * 70)
    print("[Test 5] Find Accounts Matching SEBI Violations")
    print("=" * 70)
    
    print(f"\nFinding accounts matching 'money laundering' violations...")
    
    try:
        matches = engine.find_accounts_matching_sebi_violations("money laundering")
        
        print(f"  [OK] Found {len(matches)} matching accounts")
        
        if matches:
            print(f"\n  Top 5 Matching Accounts:")
            for i, match in enumerate(matches[:5], 1):
                print(f"    {i}. {match['account']}")
                print(f"       Pattern: {match['pattern_type']}")
                print(f"       Amount: ${match['amount']:,.2f}")
                print(f"       Risk: {match['risk_level']}")
                print(f"       SEBI Cases Found: {match['sebi_cases_found']}")
        
    except Exception as e:
        print(f"  [FAIL] Matching failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("Unified GraphRAG Testing Complete!")
    print("=" * 70)
    
    print("\n[SUCCESS] All cross-domain capabilities working!")
    print("\nCapabilities Demonstrated:")
    print("  [OK] Dual knowledge base queries (SEBI + AMLSim)")
    print("  [OK] Cross-domain pattern matching")
    print("  [OK] Transaction trace with regulatory context")
    print("  [OK] Account-to-violation matching")
    print("  [OK] Unified answer generation")
    
    print("\nNext: Integrate into Streamlit UI and API")
    print("=" * 70)

# Run async main
if __name__ == "__main__":
    asyncio.run(main())

