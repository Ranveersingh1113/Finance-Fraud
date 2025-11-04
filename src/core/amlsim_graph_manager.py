"""
AMLSim Transaction Network Graph Manager.
Builds transaction network graph for money laundering detection.
Phase 4: Week 3-4 - AMLSim Integration
"""
from typing import List, Dict, Any, Optional, Tuple, Set
import logging
from pathlib import Path
import pandas as pd
import json

from .graph_manager import GraphManager

logger = logging.getLogger(__name__)


class AMLSimGraphManager(GraphManager):
    """
    AMLSim transaction network graph manager.
    
    Node Types:
    - Account: Bank accounts (individuals and corporate)
    - Customer: Account owners (individuals/organizations)
    - Alert: Suspicious activity alerts
    
    Relationship Types:
    - SENT_TO: Account → Account (money flow)
    - RECEIVED_FROM: Account ← Account (reverse tracking)
    - TRIGGERED: Account → Alert (suspicious activity)
    - OWNED_BY: Account → Customer (ownership)
    - PART_OF_PATTERN: Account → FraudRing (pattern membership)
    """
    
    def __init__(self, persist_directory: str = "./data/graphs"):
        """
        Initialize AMLSim graph manager.
        
        Args:
            persist_directory: Directory to save/load graphs
        """
        super().__init__(
            graph_name="amlsim_transaction_graph",
            persist_directory=persist_directory
        )
        
        # Statistics
        self.processed_accounts = 0
        self.processed_transactions = 0
        self.processed_alerts = 0
        self.detected_patterns = {
            'fan_out': 0,
            'fan_in': 0,
            'cycle': 0
        }
        
        logger.info("AMLSim Transaction Graph Manager initialized")
    
    def build_from_dataframes(self, accounts_df: pd.DataFrame,
                              transactions_df: pd.DataFrame,
                              alerts_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Build transaction network graph from AMLSim dataframes.
        
        Args:
            accounts_df: Account information
            transactions_df: Transaction data
            alerts_df: Alert data (optional)
            
        Returns:
            Build statistics
        """
        logger.info("Building AMLSim transaction network graph...")
        
        # Add account nodes
        self._add_account_nodes(accounts_df)
        
        # Add transaction relationships
        self._add_transaction_edges(transactions_df)
        
        # Add alerts (if provided)
        if alerts_df is not None and not alerts_df.empty:
            self._add_alert_nodes(alerts_df)
        
        stats = {
            'accounts_added': self.processed_accounts,
            'transactions_added': self.processed_transactions,
            'alerts_added': self.processed_alerts,
            'patterns_detected': self.detected_patterns
        }
        
        logger.info(f"Graph building complete: {stats}")
        return stats
    
    def _add_account_nodes(self, accounts_df: pd.DataFrame) -> None:
        """Add account nodes and customer nodes to graph."""
        logger.info(f"Adding {len(accounts_df)} account nodes...")
        
        customers_added = set()
        
        for _, account in accounts_df.iterrows():
            account_id = f"account_{account['ACCOUNT_ID']}"
            customer_id = account.get('PRIMARY_CUSTOMER_ID', '')
            
            # Add account node
            self.add_node(
                account_id,
                "Account",
                account_number=int(account['ACCOUNT_ID']),
                customer_id=customer_id,
                balance=float(account.get('init_balance', 0)),
                country=account.get('country', ''),
                business_type=account.get('business', ''),
                is_suspicious=bool(account.get('suspicious', False)),
                is_fraud=bool(account.get('isFraud', False)),
                model_id=int(account.get('modelID', 0))
            )
            
            # Add customer node if not already added
            if customer_id and customer_id not in customers_added:
                customer_node_id = f"customer_{customer_id}"
                self.add_node(
                    customer_node_id,
                    "Customer",
                    customer_id=customer_id,
                    business_type=account.get('business', ''),
                    country=account.get('country', '')
                )
                customers_added.add(customer_id)
            
            # Link account to customer
            if customer_id:
                self.add_edge(
                    account_id,
                    f"customer_{customer_id}",
                    "OWNED_BY"
                )
            
            self.processed_accounts += 1
        
        logger.info(f"Added {self.processed_accounts} account nodes and {len(customers_added)} customer nodes")
    
    def _add_transaction_edges(self, transactions_df: pd.DataFrame) -> None:
        """Add transaction edges to graph with dual relationships."""
        logger.info(f"Adding {len(transactions_df)} transaction edges...")
        
        for _, txn in transactions_df.iterrows():
            source_id = f"account_{txn['ACCOUNT_ID']}"
            dest_id = f"account_{txn['COUNTER_PARTY_ACCOUNT_NUM']}"
            
            # Ensure both accounts exist
            if source_id not in self.graph or dest_id not in self.graph:
                continue
            
            txn_properties = {
                'transaction_id': int(txn['TXN_ID']),
                'amount': float(txn['TXN_AMOUNT_ORIG']),
                'transaction_type': txn.get('TXN_SOURCE_TYPE_CODE', 'TRANSFER'),
                'timestamp': int(txn.get('start', 0)),
                'tx_count': int(txn.get('tx_count', 1))
            }
            
            # Add SENT_TO relationship (Source → Destination)
            self.add_edge(
                source_id,
                dest_id,
                "SENT_TO",
                **txn_properties
            )
            
            # Add RECEIVED_FROM relationship (Destination → Source) for easier reverse queries
            self.add_edge(
                dest_id,
                source_id,
                "RECEIVED_FROM",
                **txn_properties
            )
            
            self.processed_transactions += 1
        
        logger.info(f"Added {self.processed_transactions} transaction edges (with dual relationships)")
    
    def _add_alert_nodes(self, alerts_df: pd.DataFrame) -> None:
        """Add alert nodes and link to accounts."""
        logger.info(f"Adding {len(alerts_df)} alert nodes...")
        
        for _, alert in alerts_df.iterrows():
            alert_id = f"alert_{alert['ALERT_KEY']}"
            account_id = f"account_{alert['ACCOUNT_ID']}"
            alert_type = alert['ALERT_TEXT']
            
            # Add alert node
            self.add_node(
                alert_id,
                "Alert",
                alert_key=int(alert['ALERT_KEY']),
                alert_type=alert_type,
                account_id=int(alert['ACCOUNT_ID']),
                customer_id=alert.get('CUSTOMER_ID', ''),
                event_date=alert.get('EVENT_DATE', ''),
                check_name=alert.get('CHECK_NAME', ''),
                organization_type=alert.get('Organization_Type', ''),
                escalated=alert.get('Escalated_To_Case_Investigation', 'NO')
            )
            
            # Link alert to account
            if account_id in self.graph:
                self.add_edge(
                    account_id,
                    alert_id,
                    "TRIGGERED",
                    alert_type=alert_type
                )
            
            # Track pattern types
            if alert_type in self.detected_patterns:
                self.detected_patterns[alert_type] += 1
            
            self.processed_alerts += 1
        
        logger.info(f"Added {self.processed_alerts} alerts")
    
    def detect_fan_out_patterns(self, threshold: int = 5) -> List[Dict]:
        """
        Detect fan-out patterns (1 account → many accounts).
        
        Args:
            threshold: Minimum number of outgoing transactions to flag
            
        Returns:
            List of detected fan-out patterns
        """
        fan_out_patterns = []
        
        account_nodes = self.find_nodes_by_type('Account')
        
        for account_id in account_nodes:
            # Count outgoing transactions
            outgoing = list(self.graph.neighbors(account_id))
            
            if len(outgoing) >= threshold:
                # Get transaction details
                total_amount = 0
                transactions = []
                
                for dest in outgoing:
                    edges = self.graph[account_id][dest]
                    for edge_data in edges.values():
                        total_amount += edge_data.get('amount', 0)
                        transactions.append({
                            'destination': dest,
                            'amount': edge_data.get('amount', 0),
                            'timestamp': edge_data.get('timestamp', 0)
                        })
                
                fan_out_patterns.append({
                    'source_account': account_id,
                    'num_destinations': len(outgoing),
                    'total_amount': total_amount,
                    'transactions': transactions,
                    'pattern_type': 'fan_out',
                    'risk_level': 'HIGH' if len(outgoing) > 10 else 'MEDIUM'
                })
        
        fan_out_patterns.sort(key=lambda x: x['num_destinations'], reverse=True)
        logger.info(f"Detected {len(fan_out_patterns)} fan-out patterns")
        return fan_out_patterns
    
    def detect_fan_in_patterns(self, threshold: int = 5) -> List[Dict]:
        """
        Detect fan-in patterns (many accounts → 1 account).
        
        Args:
            threshold: Minimum number of incoming transactions to flag
            
        Returns:
            List of detected fan-in patterns
        """
        fan_in_patterns = []
        
        account_nodes = self.find_nodes_by_type('Account')
        
        for account_id in account_nodes:
            # Count incoming transactions
            incoming = list(self.graph.predecessors(account_id))
            
            if len(incoming) >= threshold:
                total_amount = 0
                transactions = []
                
                for source in incoming:
                    edges = self.graph[source][account_id]
                    for edge_data in edges.values():
                        total_amount += edge_data.get('amount', 0)
                        transactions.append({
                            'source': source,
                            'amount': edge_data.get('amount', 0),
                            'timestamp': edge_data.get('timestamp', 0)
                        })
                
                fan_in_patterns.append({
                    'destination_account': account_id,
                    'num_sources': len(incoming),
                    'total_amount': total_amount,
                    'transactions': transactions,
                    'pattern_type': 'fan_in',
                    'risk_level': 'HIGH' if len(incoming) > 10 else 'MEDIUM'
                })
        
        fan_in_patterns.sort(key=lambda x: x['num_sources'], reverse=True)
        logger.info(f"Detected {len(fan_in_patterns)} fan-in patterns")
        return fan_in_patterns
    
    def trace_money_flow(self, start_account: str, max_hops: int = 3) -> Dict[str, Any]:
        """
        Trace money flow from a specific account (ONLY outgoing transactions).
        
        Args:
            start_account: Starting account ID (e.g., 'account_631')
            max_hops: Maximum hops to trace (default 3 for performance)
            
        Returns:
            Money flow trace with paths and amounts FROM this account only
        """
        if start_account not in self.graph:
            return {
                'start_account': start_account,
                'error': 'Account not found',
                'total_sent': 0,
                'total_received': 0,
                'net_flow': 0,
                'paths': [],
                'accounts_reached': 0,
                'paths_found': 0
            }
        
        # Track ONLY direct transactions FROM this account (1-hop)
        direct_sent = []
        direct_received = []
        total_sent = 0
        total_received = 0
        
        # Get all edges FROM this account (SENT_TO relationships)
        if start_account in self.graph:
            for neighbor in self.graph.neighbors(start_account):
                edges = self.graph[start_account][neighbor]
                for edge_data in edges.values():
                    if edge_data.get('relationship') == 'SENT_TO':
                        amount = edge_data.get('amount', 0)
                        total_sent += amount
                        direct_sent.append({
                            'to': neighbor,
                            'amount': amount,
                            'timestamp': edge_data.get('timestamp', 0)
                        })
        
        # Get all edges TO this account (RECEIVED_FROM relationships)
        for predecessor in self.graph.predecessors(start_account):
            edges = self.graph[predecessor][start_account]
            for edge_data in edges.values():
                if edge_data.get('relationship') == 'SENT_TO':  # They SENT_TO us
                    amount = edge_data.get('amount', 0)
                    total_received += amount
                    direct_received.append({
                        'from': predecessor,
                        'amount': amount,
                        'timestamp': edge_data.get('timestamp', 0)
                    })
        
        # Build readable paths (limit to top 10 by amount)
        outgoing_paths = []
        for txn in sorted(direct_sent, key=lambda x: x['amount'], reverse=True)[:10]:
            outgoing_paths.append(f"{start_account} → {txn['to']} (${txn['amount']:,.2f})")
        
        incoming_paths = []
        for txn in sorted(direct_received, key=lambda x: x['amount'], reverse=True)[:10]:
            incoming_paths.append(f"{txn['from']} → {start_account} (${txn['amount']:,.2f})")
        
        # Determine unique accounts reached (1-hop only for clarity)
        accounts_reached = set()
        accounts_reached.update([txn['to'] for txn in direct_sent])
        accounts_reached.update([txn['from'] for txn in direct_received])
        
        return {
            'start_account': start_account,
            'total_hops': 1,  # Changed to 1-hop for accuracy
            'accounts_reached': len(accounts_reached),
            'paths_found': len(direct_sent) + len(direct_received),
            'total_sent': total_sent,
            'total_received': total_received,
            'net_flow': total_sent - total_received,
            'outgoing_count': len(direct_sent),
            'incoming_count': len(direct_received),
            'paths': outgoing_paths + incoming_paths,  # Readable path strings
            'top_outgoing': direct_sent[:10],
            'top_incoming': direct_received[:10]
        }
    
    def get_amlsim_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive AMLSim graph statistics.
        
        Returns:
            Dictionary with statistics
        """
        base_stats = self.get_statistics()
        
        # Count by type
        account_count = len(self.find_nodes_by_type('Account'))
        alert_count = len(self.find_nodes_by_type('Alert'))
        
        # Find suspicious accounts
        suspicious_accounts = self.find_nodes_by_property('is_suspicious', True)
        fraud_accounts = self.find_nodes_by_property('is_fraud', True)
        
        # Detect patterns
        fan_out = self.detect_fan_out_patterns(threshold=5)
        fan_in = self.detect_fan_in_patterns(threshold=5)
        
        return {
            **base_stats,
            'amlsim_specific': {
                'accounts': account_count,
                'alerts': alert_count,
                'suspicious_accounts': len(suspicious_accounts),
                'fraud_accounts': len(fraud_accounts),
                'processed_accounts': self.processed_accounts,
                'processed_transactions': self.processed_transactions,
                'processed_alerts': self.processed_alerts
            },
            'pattern_detection': {
                'fan_out_patterns': len(fan_out),
                'fan_in_patterns': len(fan_in),
                'patterns_in_alerts': self.detected_patterns
            },
            'top_fan_out': fan_out[:5] if fan_out else [],
            'top_fan_in': fan_in[:5] if fan_in else []
        }
    
    def get_ego_network(self, account_id: str, max_hops: int = 2, max_nodes: int = 200) -> Dict[str, Any]:
        """
        Extract ego network (local subgraph) for a specific account.
        Returns nodes and edges within N hops, limited to max_nodes for performance.
        
        Args:
            account_id: Account to extract network for (e.g., 'account_108')
            max_hops: Number of hops to traverse (default 2)
            max_nodes: Maximum nodes to return (default 200 for visualization performance)
            
        Returns:
            Dict with nodes, edges, and center account info
        """
        if account_id not in self.graph:
            return {
                'error': f'Account {account_id} not found',
                'nodes': [],
                'edges': [],
                'center_account': account_id
            }
        
        # BFS to find nodes within N hops
        visited = {account_id}
        current_level = {account_id}
        all_nodes = {account_id}
        
        for hop in range(max_hops):
            next_level = set()
            for node in current_level:
                # Get all neighbors (both incoming and outgoing)
                neighbors = set(self.graph.neighbors(node))
                # Also get predecessors (for directed graph)
                neighbors.update(self.graph.predecessors(node))
                
                for neighbor in neighbors:
                    if neighbor not in visited and len(all_nodes) < max_nodes:
                        visited.add(neighbor)
                        next_level.add(neighbor)
                        all_nodes.add(neighbor)
            
            current_level = next_level
            if not current_level or len(all_nodes) >= max_nodes:
                break
        
        # Extract subgraph
        subgraph = self.graph.subgraph(all_nodes)
        
        # Format nodes for frontend
        nodes = []
        for node_id in subgraph.nodes():
            node_data = self.get_node(node_id)
            if not node_data:
                continue
            
            # Determine node type and properties
            node_type = node_data.get('type', 'Unknown')
            is_center = (node_id == account_id)
            
            # Color coding based on type and flags
            color = '#3b82f6'  # blue default
            if is_center:
                color = '#ef4444'  # red for center account
            elif node_type == 'Account':
                if node_data.get('is_fraud'):
                    color = '#dc2626'  # dark red for fraud
                elif node_data.get('is_suspicious'):
                    color = '#f59e0b'  # orange for suspicious
                else:
                    color = '#10b981'  # green for normal
            elif node_type == 'Customer':
                color = '#8b5cf6'  # purple for customers
            elif node_type == 'Alert':
                color = '#f97316'  # orange for alerts
            
            # Node size based on transaction volume or importance
            size = 50 if is_center else 30
            if node_type == 'Account':
                # Scale size by balance (but keep reasonable bounds)
                balance = node_data.get('balance', 0)
                size = min(60, max(20, 20 + (balance / 100000)))
            
            nodes.append({
                'id': node_id,
                'label': node_id.replace('account_', 'A').replace('customer_', 'C').replace('alert_', 'Alert'),
                'type': node_type,
                'color': color,
                'size': size,
                'is_center': is_center,
                'data': {
                    'balance': node_data.get('balance', 0),
                    'country': node_data.get('country', ''),
                    'business_type': node_data.get('business_type', ''),
                    'is_suspicious': node_data.get('is_suspicious', False),
                    'is_fraud': node_data.get('is_fraud', False)
                }
            })
        
        # Format edges for frontend
        edges = []
        edge_id = 0
        for source, target, edge_data in subgraph.edges(data=True):
            # Only include SENT_TO relationships (skip RECEIVED_FROM to avoid duplicates)
            if edge_data.get('relationship_type') == 'SENT_TO':
                amount = edge_data.get('amount', 0)
                
                # Edge thickness based on transaction amount
                width = min(10, max(1, amount / 10000))
                
                edges.append({
                    'id': f'edge_{edge_id}',
                    'source': source,
                    'target': target,
                    'label': f'${amount:,.0f}',
                    'width': width,
                    'type': edge_data.get('relationship_type', 'SENT_TO'),
                    'data': {
                        'amount': amount,
                        'transaction_type': edge_data.get('transaction_type', ''),
                        'timestamp': edge_data.get('timestamp', 0)
                    }
                })
                edge_id += 1
        
        logger.info(f"Extracted ego network for {account_id}: {len(nodes)} nodes, {len(edges)} edges")
        
        return {
            'center_account': account_id,
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'hops': max_hops,
                'account_nodes': sum(1 for n in nodes if n['type'] == 'Account'),
                'suspicious_nodes': sum(1 for n in nodes if n.get('data', {}).get('is_suspicious')),
                'fraud_nodes': sum(1 for n in nodes if n.get('data', {}).get('is_fraud'))
            }
        }
    
    def extract_fraud_patterns(self, max_hops: int = 2) -> List[Dict]:
        """
        Extract fraud ring patterns from suspicious accounts.
        Uses AMLSim SAR labels to identify fraud rings.
        
        Args:
            max_hops: Maximum hops to explore from suspicious account
            
        Returns:
            List of fraud ring patterns with members and transactions
        """
        fraud_patterns = []
        
        # Get all suspicious/fraud accounts
        suspicious_accounts = self.find_nodes_by_property('is_fraud', True)
        
        logger.info(f"Extracting fraud patterns from {len(suspicious_accounts)} suspicious accounts...")
        
        for account_id in suspicious_accounts:
            # Get fraud ring using multi-hop traversal
            ring_data = self.multi_hop_query(account_id, max_hops=max_hops)
            
            # Calculate ring statistics
            total_amount = 0
            outgoing_count = 0
            incoming_count = 0
            
            for rel in ring_data['relationships']:
                amount = rel['properties'].get('amount', 0)
                total_amount += amount
                
                if rel['source'] == account_id:
                    outgoing_count += 1
                if rel['target'] == account_id:
                    incoming_count += 1
            
            # Identify pattern type
            pattern_type = self._identify_pattern_type(outgoing_count, incoming_count)
            
            fraud_patterns.append({
                'pattern_id': f"fraud_ring_{account_id}",
                'core_account': account_id,
                'ring_members': list(ring_data['nodes']),
                'member_count': ring_data['total_nodes'],
                'transaction_paths': ring_data['total_paths'],
                'total_amount': total_amount,
                'outgoing_transactions': outgoing_count,
                'incoming_transactions': incoming_count,
                'pattern_type': pattern_type,
                'risk_level': self._calculate_risk_level(outgoing_count, incoming_count, total_amount)
            })
        
        # Sort by risk
        fraud_patterns.sort(key=lambda x: x['total_amount'], reverse=True)
        
        logger.info(f"Extracted {len(fraud_patterns)} fraud ring patterns")
        return fraud_patterns
    
    def _identify_pattern_type(self, outgoing: int, incoming: int) -> str:
        """
        Identify money laundering pattern type based on transaction flow.
        
        Args:
            outgoing: Number of outgoing transactions
            incoming: Number of incoming transactions
            
        Returns:
            Pattern type name
        """
        ratio = outgoing / max(incoming, 1)
        
        if outgoing > 10 and ratio > 3:
            return "fan_out"  # Placement/Structuring
        elif incoming > 10 and ratio < 0.3:
            return "fan_in"  # Integration/Collection
        elif outgoing > 5 and incoming > 5 and 0.5 < ratio < 2:
            return "cycle_hub"  # Layering hub
        elif outgoing > 0 and incoming > 0:
            return "intermediary"  # Layering intermediary
        else:
            return "unknown"
    
    def _calculate_risk_level(self, outgoing: int, incoming: int, amount: float) -> str:
        """Calculate risk level for a pattern."""
        if amount > 500000 or outgoing > 20 or incoming > 20:
            return "CRITICAL"
        elif amount > 100000 or outgoing > 10 or incoming > 10:
            return "HIGH"
        elif amount > 50000 or outgoing > 5 or incoming > 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def export_for_pyvis(self, output_file: str = None, 
                        include_all_accounts: bool = False) -> str:
        """
        Export graph for interactive Pyvis visualization.
        
        Args:
            output_file: Output HTML file path
            include_all_accounts: If False, only show suspicious accounts and their connections
            
        Returns:
            Path to generated HTML file
        """
        try:
            from pyvis.network import Network
        except ImportError:
            logger.error("Pyvis not installed. Run: pip install pyvis")
            return ""
        
        if output_file is None:
            output_file = self.persist_directory / "amlsim_network_visualization.html"
        
        # Create network
        net = Network(
            height='800px',
            width='100%',
            directed=True,
            bgcolor='#222222',
            font_color='white'
        )
        
        # Determine which nodes to include
        if include_all_accounts:
            nodes_to_include = set(self.graph.nodes())
        else:
            # Only suspicious accounts and their immediate connections
            suspicious = self.find_nodes_by_property('is_suspicious', True)
            nodes_to_include = set()
            for acc in suspicious:
                nodes_to_include.add(acc)
                # Add neighbors
                nodes_to_include.update(self.graph.neighbors(acc))
                nodes_to_include.update(self.graph.predecessors(acc))
        
        # Add nodes to visualization
        for node_id in nodes_to_include:
            if node_id not in self.graph:
                continue
            
            node_data = self.get_node(node_id)
            node_type = node_data.get('type', 'Unknown')
            
            # Color by type and suspicion
            if node_type == 'Alert':
                color = '#FF4444'  # Red for alerts
                size = 25
            elif node_type == 'Customer':
                color = '#4444FF'  # Blue for customers
                size = 20
            elif node_data.get('is_fraud'):
                color = '#FF0000'  # Bright red for fraud
                size = 30
            elif node_data.get('is_suspicious'):
                color = '#FF8800'  # Orange for suspicious
                size = 25
            else:
                color = '#00AA00'  # Green for normal
                size = 15
            
            # Create label
            if node_type == 'Account':
                label = f"Acc_{node_data.get('account_number', '')}"
            elif node_type == 'Customer':
                label = node_data.get('customer_id', node_id)
            else:
                label = node_id
            
            # Create hover tooltip
            title = f"{node_type}\n"
            for key, value in node_data.items():
                if key not in ['type', 'created_at']:
                    title += f"{key}: {value}\n"
            
            net.add_node(
                node_id,
                label=label,
                color=color,
                size=size,
                title=title
            )
        
        # Add edges
        for source, target, data in self.graph.edges(data=True):
            if source not in nodes_to_include or target not in nodes_to_include:
                continue
            
            rel_type = data.get('relationship', 'UNKNOWN')
            amount = data.get('amount', 0)
            
            # Color by relationship type
            if rel_type == 'TRIGGERED':
                color = '#FF0000'
                width = 3
            elif rel_type == 'SENT_TO':
                color = '#00FF00'
                width = max(1, min(10, amount / 10000))  # Scale by amount
            elif rel_type == 'RECEIVED_FROM':
                color = '#0088FF'
                width = max(1, min(10, amount / 10000))
            else:
                color = '#888888'
                width = 1
            
            # Create edge label
            if amount > 0:
                label = f"${amount:,.0f}"
            else:
                label = rel_type
            
            net.add_edge(
                source,
                target,
                label=label,
                color=color,
                width=width,
                title=f"{rel_type}: ${amount:,.2f}"
            )
        
        # Set physics options
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -8000,
              "centralGravity": 0.3,
              "springLength": 95
            }
          },
          "edges": {
            "smooth": {
              "type": "continuous"
            }
          }
        }
        """)
        
        # Generate HTML
        net.save_graph(str(output_file))
        logger.info(f"Pyvis visualization exported to: {output_file}")
        
        return str(output_file)

