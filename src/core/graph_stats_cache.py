"""
Cached graph statistics for O(1) access instead of O(N) scans.
Reduces context gathering time from 5-10s to <100ms.
"""
import time
import logging
from typing import Dict, Any, Optional

from .rag_config import RAGConfig

logger = logging.getLogger(__name__)


class GraphStatsCache:
    """
    Cached graph statistics with auto-refresh.
    
    Prevents expensive O(N) full-graph scans on every query by caching statistics
    and refreshing them periodically.
    """
    
    def __init__(self, graph_manager, ttl: int = RAGConfig.STATS_CACHE_TTL):
        """
        Initialize graph stats cache.
        
        Args:
            graph_manager: Graph manager instance (SEBI or AMLSim)
            ttl: Time-to-live for cached stats in seconds
        """
        self.graph = graph_manager
        self.ttl = ttl
        self._stats: Optional[Dict[str, Any]] = None
        self._last_update: float = 0
        self.graph_type = self._detect_graph_type()
        
        logger.info(f"Initialized GraphStatsCache for {self.graph_type} (ttl={ttl}s)")
    
    def _detect_graph_type(self) -> str:
        """Detect whether this is a SEBI or AMLSim graph."""
        graph_class_name = self.graph.__class__.__name__
        if 'SEBI' in graph_class_name:
            return 'sebi'
        elif 'AMLSim' in graph_class_name:
            return 'amlsim'
        else:
            return 'unknown'
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cached stats or compute if stale.
        
        Returns:
            Dictionary with graph statistics
        """
        current_time = time.time()
        
        # Check if cache is stale
        if self._stats is None or (current_time - self._last_update) > self.ttl:
            logger.info(f"Computing {self.graph_type} graph statistics (cache stale or empty)")
            self._stats = self._compute_stats()
            self._last_update = current_time
        else:
            logger.debug(f"Using cached {self.graph_type} stats (age: {current_time - self._last_update:.1f}s)")
        
        return self._stats
    
    def _compute_stats(self) -> Dict[str, Any]:
        """
        Compute stats once, cache for TTL.
        
        Returns:
            Dictionary with computed statistics
        """
        try:
            start_time = time.time()
            
            if self.graph_type == 'sebi':
                stats = self._compute_sebi_stats()
            elif self.graph_type == 'amlsim':
                stats = self._compute_amlsim_stats()
            else:
                stats = self._compute_generic_stats()
            
            elapsed = time.time() - start_time
            logger.info(f"Computed {self.graph_type} stats in {elapsed:.3f}s")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error computing {self.graph_type} stats: {e}")
            return {
                'available': False,
                'error': str(e),
                'total_nodes': 0,
                'total_edges': 0
            }
    
    def _compute_sebi_stats(self) -> Dict[str, Any]:
        """Compute SEBI-specific statistics."""
        try:
            # Get node counts by type
            entities = self.graph.find_nodes_by_type('Entity')
            persons = self.graph.find_nodes_by_type('Person')
            violations = self.graph.find_nodes_by_type('Violation')
            
            total_entities = len(entities) + len(persons)
            
            # Get graph totals
            total_nodes = len(self.graph.graph.nodes())
            total_edges = len(self.graph.graph.edges())
            
            return {
                'available': True,
                'total_entities': total_entities,
                'entity_count': len(entities),
                'person_count': len(persons),
                'total_violations': len(violations),
                'total_nodes': total_nodes,
                'total_edges': total_edges,
                'graph_type': 'sebi'
            }
        except Exception as e:
            logger.error(f"Error computing SEBI stats: {e}")
            return {
                'available': False,
                'error': str(e),
                'total_entities': 0,
                'total_violations': 0,
                'total_nodes': 0,
                'total_edges': 0
            }
    
    def _compute_amlsim_stats(self) -> Dict[str, Any]:
        """Compute AMLSim-specific statistics."""
        try:
            # Get node counts
            account_nodes = self.graph.find_nodes_by_type('Account')
            suspicious = self.graph.find_nodes_by_property('is_suspicious', True)
            fraud_accounts = self.graph.find_nodes_by_property('is_fraud', True)
            
            # Get graph totals
            total_nodes = len(self.graph.graph.nodes())
            total_edges = len(self.graph.graph.edges())
            
            return {
                'available': True,
                'total_accounts': len(account_nodes),
                'suspicious_accounts': len(suspicious),
                'fraud_accounts': len(fraud_accounts),
                'total_nodes': total_nodes,
                'total_edges': total_edges,
                'graph_type': 'amlsim'
            }
        except Exception as e:
            logger.error(f"Error computing AMLSim stats: {e}")
            return {
                'available': False,
                'error': str(e),
                'total_accounts': 0,
                'suspicious_accounts': 0,
                'total_nodes': 0,
                'total_edges': 0
            }
    
    def _compute_generic_stats(self) -> Dict[str, Any]:
        """Compute generic graph statistics."""
        try:
            total_nodes = len(self.graph.graph.nodes())
            total_edges = len(self.graph.graph.edges())
            
            return {
                'available': True,
                'total_nodes': total_nodes,
                'total_edges': total_edges,
                'graph_type': 'generic'
            }
        except Exception as e:
            logger.error(f"Error computing generic stats: {e}")
            return {
                'available': False,
                'error': str(e),
                'total_nodes': 0,
                'total_edges': 0
            }
    
    def invalidate(self) -> None:
        """Invalidate the cache, forcing a recompute on next access."""
        self._stats = None
        self._last_update = 0
        logger.info(f"Invalidated {self.graph_type} stats cache")
    
    def refresh(self) -> Dict[str, Any]:
        """
        Force refresh the cache.
        
        Returns:
            Newly computed statistics
        """
        self.invalidate()
        return self.get_stats()
    
    def get_cache_age(self) -> float:
        """
        Get age of cached data in seconds.
        
        Returns:
            Age in seconds, or -1 if no cache
        """
        if self._stats is None:
            return -1
        return time.time() - self._last_update
    
    def is_stale(self) -> bool:
        """
        Check if cache is stale.
        
        Returns:
            True if cache is stale or empty
        """
        if self._stats is None:
            return True
        return (time.time() - self._last_update) > self.ttl

