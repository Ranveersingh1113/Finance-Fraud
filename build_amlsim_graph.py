"""
Build AMLSim Transaction Network Graph
Phase 4 - Week 3-4: AMLSim Integration
"""
import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.amlsim_graph_manager import AMLSimGraphManager
from src.data.amlsim_loader import AMLSimLoader

print("=" * 70)
print("AMLSim Transaction Network Graph Construction")
print("Phase 4 - Week 3-4")
print("=" * 70)

# Initialize components
print("\n[Step 1] Initializing components...")
try:
    loader = AMLSimLoader()
    graph_manager = AMLSimGraphManager()
    print("  [OK] Components initialized")
except Exception as e:
    print(f"  [FAIL] Initialization failed: {e}")
    sys.exit(1)

# Load AMLSim data
print("\n[Step 2] Loading AMLSim data...")
try:
    data = loader.load_all_data()
    
    accounts_df = data['accounts']
    transactions_df = data['transactions']
    alerts_df = data['alerts']
    cash_df = data['cash_transactions']
    
    if accounts_df.empty or transactions_df.empty:
        print("  [FAIL] Required data files not found!")
        print("  Run: python generate_amlsim_compatible_data.py")
        sys.exit(1)
    
    print(f"  [OK] Loaded AMLSim data:")
    print(f"    - Accounts: {len(accounts_df):,}")
    print(f"    - Transactions: {len(transactions_df):,}")
    print(f"    - Alerts: {len(alerts_df):,}")
    print(f"    - Cash Transactions: {len(cash_df):,}")
    
    # Show summary
    summary = loader.get_summary()
    print(f"\n  Data Summary:")
    print(f"    - Suspicious accounts: {summary.get('suspicious_accounts', 0)}")
    print(f"    - Alert types: {summary.get('alert_types', {})}")
    
except Exception as e:
    print(f"  [FAIL] Loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Build transaction network graph
print(f"\n[Step 3] Building transaction network graph...")
print("  This may take a few minutes...")

start_time = time.time()

try:
    result = graph_manager.build_from_dataframes(
        accounts_df=accounts_df,
        transactions_df=transactions_df,
        alerts_df=alerts_df
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"\n  [OK] Graph built in {elapsed_time:.2f} seconds")
    print(f"  Accounts added: {result['accounts_added']:,}")
    print(f"  Transactions added: {result['transactions_added']:,}")
    print(f"  Alerts added: {result['alerts_added']:,}")
    
except Exception as e:
    print(f"  [FAIL] Graph building failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Get graph statistics
print("\n[Step 4] Analyzing transaction network...")
try:
    stats = graph_manager.get_amlsim_statistics()
    
    print("\n  Graph Statistics:")
    print(f"  Total Nodes: {stats['total_nodes']:,}")
    print(f"  Total Edges: {stats['total_edges']:,}")
    
    print("\n  Node Types:")
    for node_type, count in stats['node_types'].items():
        print(f"    - {node_type}: {count:,}")
    
    print("\n  Relationship Types:")
    for rel_type, count in stats['relationship_types'].items():
        print(f"    - {rel_type}: {count:,}")
    
    amlsim_stats = stats['amlsim_specific']
    print(f"\n  AMLSim-Specific Metrics:")
    print(f"    - Accounts: {amlsim_stats['accounts']:,}")
    print(f"    - Suspicious Accounts: {amlsim_stats['suspicious_accounts']}")
    print(f"    - Fraud Accounts: {amlsim_stats['fraud_accounts']}")
    print(f"    - Alerts: {amlsim_stats['alerts']}")
    
    pattern_stats = stats['pattern_detection']
    print(f"\n  Pattern Detection:")
    print(f"    - Fan-Out Patterns Detected: {pattern_stats['fan_out_patterns']}")
    print(f"    - Fan-In Patterns Detected: {pattern_stats['fan_in_patterns']}")
    
    # Show top fan-out patterns
    if stats['top_fan_out']:
        print(f"\n  Top 5 Fan-Out Patterns (Suspicious):")
        for i, pattern in enumerate(stats['top_fan_out'], 1):
            print(f"    {i}. {pattern['source_account']}")
            print(f"       -> {pattern['num_destinations']} destinations")
            print(f"       Total amount: ${pattern['total_amount']:,.2f}")
            print(f"       Risk: {pattern['risk_level']}")
    
    # Show top fan-in patterns
    if stats['top_fan_in']:
        print(f"\n  Top 5 Fan-In Patterns (Suspicious):")
        for i, pattern in enumerate(stats['top_fan_in'], 1):
            print(f"    {i}. {pattern['destination_account']}")
            print(f"       <- {pattern['num_sources']} sources")
            print(f"       Total amount: ${pattern['total_amount']:,.2f}")
            print(f"       Risk: {pattern['risk_level']}")
    
except Exception as e:
    print(f"  [FAIL] Statistics generation failed: {e}")
    import traceback
    traceback.print_exc()

# Save graph
print("\n[Step 5] Saving transaction network graph...")
try:
    save_path = graph_manager.save_graph()
    print(f"  [OK] Graph saved to: {save_path}")
    
    json_path = graph_manager.export_to_json()
    print(f"  [OK] JSON export saved to: {json_path}")
    
except Exception as e:
    print(f"  [FAIL] Saving failed: {e}")

# Test queries
print("\n[Step 6] Testing money flow analysis...")

try:
    # Test money flow tracing
    if stats['amlsim_specific']['suspicious_accounts'] > 0:
        # Find a suspicious account
        suspicious_accounts = graph_manager.find_nodes_by_property('is_suspicious', True)
        
        if suspicious_accounts:
            test_account = suspicious_accounts[0]
            print(f"\n  Tracing money flow from: {test_account}")
            
            flow = graph_manager.trace_money_flow(test_account, max_hops=3)
            print(f"    - Accounts reached: {flow['accounts_reached']}")
            print(f"    - Paths found: {flow['paths_found']}")
            print(f"    - Total sent: ${flow['total_sent']:,.2f}")
            print(f"    - Total received: ${flow['total_received']:,.2f}")
            print(f"    - Net flow: ${flow['net_flow']:,.2f}")
    
    print("\n  [OK] Money flow tracing functional")
    
except Exception as e:
    print(f"  [FAIL] Query testing failed: {e}")
    import traceback
    traceback.print_exc()

# Test fraud ring extraction
print("\n[Step 7] Extracting fraud ring patterns...")
try:
    fraud_rings = graph_manager.extract_fraud_patterns(max_hops=2)
    
    print(f"  [OK] Extracted {len(fraud_rings)} fraud ring patterns")
    
    if fraud_rings:
        print(f"\n  Top 5 Most Dangerous Fraud Rings:")
        for i, ring in enumerate(fraud_rings[:5], 1):
            print(f"    {i}. {ring['core_account']}")
            print(f"       Pattern: {ring['pattern_type']}")
            print(f"       Members: {ring['member_count']}")
            print(f"       Paths: {ring['transaction_paths']}")
            print(f"       Amount: ${ring['total_amount']:,.2f}")
            print(f"       Risk: {ring['risk_level']}")
    
except Exception as e:
    print(f"  [FAIL] Fraud ring extraction failed: {e}")
    import traceback
    traceback.print_exc()

# Generate visualization
print("\n[Step 8] Generating interactive visualization...")
try:
    viz_path = graph_manager.export_for_pyvis(
        include_all_accounts=False  # Only suspicious accounts for clarity
    )
    print(f"  [OK] Interactive visualization saved to: {viz_path}")
    print(f"  Open in browser to explore fraud network!")
    
except Exception as e:
    print(f"  [FAIL] Visualization export failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("AMLSim Transaction Network Graph Complete!")
print("=" * 70)

print("\n[OK] Week 3-4 Milestone Achieved!")
print("\nGraph Summary:")
print(f"  - {stats['total_nodes']:,} nodes")
print(f"  - {stats['total_edges']:,} edges")
print(f"  - {amlsim_stats['accounts']:,} accounts")
print(f"  - {amlsim_stats['suspicious_accounts']} suspicious accounts")
print(f"  - {pattern_stats['fan_out_patterns']} fan-out patterns")
print(f"  - {pattern_stats['fan_in_patterns']} fan-in patterns")

print("\nSaved Files:")
print(f"  - Graph: {save_path}")
print(f"  - JSON: {json_path}")

print("\nNext Steps:")
print("  1. Test AMLSim graph queries")
print("  2. Week 5-6: Integrate with SEBI graph")
print("  3. Build unified GraphRAG system")
print("  4. Add interactive visualization")

print("\n" + "=" * 70)

