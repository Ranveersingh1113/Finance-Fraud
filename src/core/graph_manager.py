"""
Base Graph Manager for Financial Intelligence Platform.
Provides common graph operations using NetworkX.
Phase 4: GraphRAG & Network Intelligence
"""
import networkx as nx
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class GraphManager:
    """
    Base class for graph management using NetworkX.
    
    Provides common operations for:
    - Graph creation and persistence
    - Node and edge management
    - Graph queries and traversals
    - Graph statistics and analysis
    """
    
    def __init__(self, graph_name: str = "knowledge_graph", 
                 persist_directory: str = "./data/graphs"):
        """
        Initialize graph manager.
        
        Args:
            graph_name: Name of the graph (used for persistence)
            persist_directory: Directory to save/load graphs
        """
        self.graph_name = graph_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize directed multigraph (allows multiple edges between nodes)
        self.graph = nx.MultiDiGraph()
        
        # Metadata
        self.created_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
        
        logger.info(f"GraphManager initialized: {graph_name}")
    
    def add_node(self, node_id: str, node_type: str, **properties) -> None:
        """
        Add a node to the graph with properties.
        
        Args:
            node_id: Unique identifier for the node
            node_type: Type of node (e.g., 'Entity', 'Violation', 'Card')
            **properties: Additional node properties
        """
        properties['type'] = node_type
        properties['created_at'] = datetime.now().isoformat()
        self.graph.add_node(node_id, **properties)
        self.last_updated = datetime.now().isoformat()
    
    def add_edge(self, source_id: str, target_id: str, 
                 relationship: str, **properties) -> None:
        """
        Add an edge (relationship) between two nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            relationship: Type of relationship
            **properties: Additional edge properties
        """
        properties['relationship'] = relationship
        properties['created_at'] = datetime.now().isoformat()
        self.graph.add_edge(source_id, target_id, **properties)
        self.last_updated = datetime.now().isoformat()
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """
        Get node data by ID.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Node data dictionary or None
        """
        if node_id in self.graph:
            return dict(self.graph.nodes[node_id])
        return None
    
    def get_neighbors(self, node_id: str, relationship_type: str = None) -> List[str]:
        """
        Get neighboring nodes connected to the given node.
        
        Args:
            node_id: Node identifier
            relationship_type: Optional filter by relationship type
            
        Returns:
            List of neighbor node IDs
        """
        if node_id not in self.graph:
            return []
        
        if relationship_type:
            # Filter by relationship type
            neighbors = []
            for neighbor in self.graph.neighbors(node_id):
                edges = self.graph[node_id][neighbor]
                for edge_data in edges.values():
                    if edge_data.get('relationship') == relationship_type:
                        neighbors.append(neighbor)
                        break
            return neighbors
        else:
            return list(self.graph.neighbors(node_id))
    
    def multi_hop_query(self, start_node: str, max_hops: int = 2,
                       relationship_filter: List[str] = None) -> Dict[str, Any]:
        """
        Perform multi-hop graph traversal starting from a node.
        
        Args:
            start_node: Starting node ID
            max_hops: Maximum number of hops to traverse
            relationship_filter: Optional list of relationship types to follow
            
        Returns:
            Dictionary with paths and connected nodes
        """
        if start_node not in self.graph:
            return {'paths': [], 'nodes': set(), 'relationships': []}
        
        visited = set()
        paths = []
        all_relationships = []
        
        def _traverse(current, path, hop):
            if hop > max_hops:
                return
            
            visited.add(current)
            
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited or hop < max_hops:
                    # Get edge data
                    edges = self.graph[current][neighbor]
                    for edge_data in edges.values():
                        rel_type = edge_data.get('relationship')
                        
                        # Apply relationship filter
                        if relationship_filter and rel_type not in relationship_filter:
                            continue
                        
                        new_path = path + [(current, rel_type, neighbor)]
                        paths.append(new_path)
                        all_relationships.append({
                            'source': current,
                            'relationship': rel_type,
                            'target': neighbor,
                            'properties': edge_data
                        })
                        
                        if hop < max_hops:
                            _traverse(neighbor, new_path, hop + 1)
        
        _traverse(start_node, [], 0)
        
        return {
            'start_node': start_node,
            'paths': paths,
            'nodes': visited,
            'relationships': all_relationships,
            'total_paths': len(paths),
            'total_nodes': len(visited)
        }
    
    def find_nodes_by_type(self, node_type: str) -> List[str]:
        """
        Find all nodes of a specific type.
        
        Args:
            node_type: Type of nodes to find
            
        Returns:
            List of node IDs
        """
        return [node for node, data in self.graph.nodes(data=True)
                if data.get('type') == node_type]
    
    def find_nodes_by_property(self, property_name: str, 
                               property_value: Any) -> List[str]:
        """
        Find nodes with a specific property value.
        
        Args:
            property_name: Property name to search
            property_value: Property value to match
            
        Returns:
            List of node IDs
        """
        return [node for node, data in self.graph.nodes(data=True)
                if data.get(property_name) == property_value]
    
    def get_subgraph(self, node_ids: List[str]) -> nx.MultiDiGraph:
        """
        Extract a subgraph containing specified nodes.
        
        Args:
            node_ids: List of node IDs to include
            
        Returns:
            Subgraph as NetworkX MultiDiGraph
        """
        return self.graph.subgraph(node_ids).copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive graph statistics.
        
        Returns:
            Dictionary with graph statistics
        """
        node_types = {}
        relationship_types = {}
        
        # Count node types
        for node, data in self.graph.nodes(data=True):
            node_type = data.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Count relationship types
        for u, v, data in self.graph.edges(data=True):
            rel_type = data.get('relationship', 'unknown')
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
        
        return {
            'graph_name': self.graph_name,
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': node_types,
            'relationship_types': relationship_types,
            'is_directed': self.graph.is_directed(),
            'is_multigraph': self.graph.is_multigraph(),
            'created_at': self.created_at,
            'last_updated': self.last_updated
        }
    
    def save_graph(self, file_path: str = None) -> str:
        """
        Save graph to disk using pickle.
        
        Args:
            file_path: Optional custom file path
            
        Returns:
            Path where graph was saved
        """
        if file_path is None:
            file_path = self.persist_directory / f"{self.graph_name}.gpickle"
        else:
            file_path = Path(file_path)
        
        try:
            with open(file_path, 'wb') as f:
                pickle.dump({
                    'graph': self.graph,
                    'metadata': {
                        'graph_name': self.graph_name,
                        'created_at': self.created_at,
                        'last_updated': self.last_updated
                    }
                }, f)
            
            logger.info(f"Graph saved to {file_path}")
            return str(file_path)
        
        except Exception as e:
            logger.error(f"Error saving graph: {e}")
            raise
    
    def load_graph(self, file_path: str = None) -> bool:
        """
        Load graph from disk.
        
        Args:
            file_path: Optional custom file path
            
        Returns:
            True if successful
        """
        if file_path is None:
            file_path = self.persist_directory / f"{self.graph_name}.gpickle"
        else:
            file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"Graph file not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                self.graph = data['graph']
                metadata = data.get('metadata', {})
                self.graph_name = metadata.get('graph_name', self.graph_name)
                self.created_at = metadata.get('created_at', self.created_at)
                self.last_updated = metadata.get('last_updated', self.last_updated)
            
            logger.info(f"Graph loaded from {file_path}")
            logger.info(f"Nodes: {self.graph.number_of_nodes()}, "
                       f"Edges: {self.graph.number_of_edges()}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading graph: {e}")
            return False
    
    def export_to_json(self, file_path: str = None) -> str:
        """
        Export graph to JSON format for visualization.
        
        Args:
            file_path: Optional custom file path
            
        Returns:
            Path where JSON was saved
        """
        if file_path is None:
            file_path = self.persist_directory / f"{self.graph_name}.json"
        else:
            file_path = Path(file_path)
        
        # Convert graph to node-link format
        data = nx.node_link_data(self.graph)
        
        # Add metadata
        data['metadata'] = {
            'graph_name': self.graph_name,
            'created_at': self.created_at,
            'last_updated': self.last_updated,
            'statistics': self.get_statistics()
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Graph exported to JSON: {file_path}")
            return str(file_path)
        
        except Exception as e:
            logger.error(f"Error exporting graph to JSON: {e}")
            raise
    
    def clear_graph(self) -> None:
        """Clear all nodes and edges from the graph."""
        self.graph.clear()
        self.last_updated = datetime.now().isoformat()
        logger.info(f"Graph cleared: {self.graph_name}")
    
    def __repr__(self) -> str:
        return (f"GraphManager(name='{self.graph_name}', "
                f"nodes={self.graph.number_of_nodes()}, "
                f"edges={self.graph.number_of_edges()})")

