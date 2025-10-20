"""
Circuit breaker pattern for resilient graph operations.
Prevents cascading failures when graph services become unavailable.
"""
import time
import logging
from typing import Optional

from .rag_config import RAGConfig

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures in graph operations.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failure threshold exceeded, requests are blocked
    - HALF_OPEN: Testing if service has recovered
    """
    
    STATE_CLOSED = "CLOSED"
    STATE_OPEN = "OPEN"
    STATE_HALF_OPEN = "HALF_OPEN"
    
    def __init__(self, 
                 name: str,
                 failure_threshold: int = RAGConfig.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                 timeout: int = RAGConfig.CIRCUIT_BREAKER_TIMEOUT,
                 half_open_attempts: int = 1):
        """
        Initialize circuit breaker.
        
        Args:
            name: Name of the circuit (for logging)
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting to close circuit
            half_open_attempts: Number of successful attempts needed to close circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_attempts = half_open_attempts
        
        # State tracking
        self.failure_count = 0
        self.success_count = 0
        self.state = self.STATE_CLOSED
        self.opened_at: Optional[float] = None
        self.last_failure_time: Optional[float] = None
        
        logger.info(f"Initialized CircuitBreaker '{name}' "
                   f"(threshold={failure_threshold}, timeout={timeout}s)")
    
    def is_open(self) -> bool:
        """
        Check if circuit is open (blocking requests).
        
        Returns:
            True if circuit is open
        """
        # If circuit is open, check if timeout has elapsed
        if self.state == self.STATE_OPEN:
            if self.opened_at and (time.time() - self.opened_at) >= self.timeout:
                # Move to half-open state to test if service recovered
                self._transition_to_half_open()
                return False
            return True
        
        return False
    
    def is_closed(self) -> bool:
        """
        Check if circuit is closed (normal operation).
        
        Returns:
            True if circuit is closed
        """
        return self.state == self.STATE_CLOSED
    
    def is_half_open(self) -> bool:
        """
        Check if circuit is half-open (testing recovery).
        
        Returns:
            True if circuit is half-open
        """
        return self.state == self.STATE_HALF_OPEN
    
    def record_success(self) -> None:
        """Record a successful operation."""
        if self.state == self.STATE_HALF_OPEN:
            self.success_count += 1
            logger.info(f"CircuitBreaker '{self.name}': Success in HALF_OPEN state "
                       f"({self.success_count}/{self.half_open_attempts})")
            
            # If enough successes, close the circuit
            if self.success_count >= self.half_open_attempts:
                self._transition_to_closed()
        
        elif self.state == self.STATE_CLOSED:
            # Reset failure count on success
            if self.failure_count > 0:
                logger.debug(f"CircuitBreaker '{self.name}': Resetting failure count "
                           f"after success (was {self.failure_count})")
                self.failure_count = 0
    
    def record_failure(self) -> None:
        """Record a failed operation."""
        self.last_failure_time = time.time()
        
        if self.state == self.STATE_HALF_OPEN:
            # Failure in half-open state reopens the circuit
            logger.warning(f"CircuitBreaker '{self.name}': Failure in HALF_OPEN state, "
                          f"reopening circuit")
            self._transition_to_open()
        
        elif self.state == self.STATE_CLOSED:
            self.failure_count += 1
            logger.warning(f"CircuitBreaker '{self.name}': Failure recorded "
                          f"({self.failure_count}/{self.failure_threshold})")
            
            # Check if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()
    
    def _transition_to_open(self) -> None:
        """Transition to OPEN state."""
        self.state = self.STATE_OPEN
        self.opened_at = time.time()
        self.success_count = 0
        
        logger.error(f"CircuitBreaker '{self.name}': OPENED after {self.failure_count} failures. "
                    f"Will retry after {self.timeout}s")
    
    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self.state = self.STATE_HALF_OPEN
        self.success_count = 0
        
        logger.info(f"CircuitBreaker '{self.name}': Transitioning to HALF_OPEN state "
                   f"(testing recovery)")
    
    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self.state = self.STATE_CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.opened_at = None
        
        logger.info(f"CircuitBreaker '{self.name}': CLOSED (service recovered)")
    
    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        logger.info(f"CircuitBreaker '{self.name}': Manual reset")
        self._transition_to_closed()
    
    def get_state(self) -> dict:
        """
        Get current state of the circuit breaker.
        
        Returns:
            Dictionary with state information
        """
        return {
            'name': self.name,
            'state': self.state,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'success_count': self.success_count,
            'opened_at': self.opened_at,
            'last_failure_time': self.last_failure_time,
            'time_until_retry': (
                self.timeout - (time.time() - self.opened_at)
                if self.opened_at and self.state == self.STATE_OPEN
                else 0
            )
        }
    
    def __str__(self) -> str:
        """String representation of circuit breaker state."""
        return (f"CircuitBreaker(name='{self.name}', state={self.state}, "
                f"failures={self.failure_count}/{self.failure_threshold})")

