"""
Input Validators
Validation and sanitization utilities for user inputs.
"""

import re
from typing import Optional


class AccountIDValidator:
    """
    Validate and sanitize account IDs.
    
    Prevents injection attacks and ensures valid account references.
    """
    
    # Valid account ID range
    MIN_ACCOUNT_ID = 0
    MAX_ACCOUNT_ID = 999999
    
    @staticmethod
    def validate(account_id: str) -> int:
        """
        Validate and sanitize an account ID.
        
        Args:
            account_id: Raw account ID input (may contain non-numeric chars)
            
        Returns:
            Validated account ID as integer
            
        Raises:
            ValueError: If account ID is invalid
        """
        if not account_id:
            raise ValueError("Account ID cannot be empty")
        
        # Remove any non-digit characters for safety
        clean_id = re.sub(r'\D', '', str(account_id))
        
        if not clean_id:
            raise ValueError(f"Account ID must contain digits: '{account_id}'")
        
        try:
            account_num = int(clean_id)
        except ValueError:
            raise ValueError(f"Invalid account ID format: '{account_id}'")
        
        # Range validation
        if account_num < AccountIDValidator.MIN_ACCOUNT_ID:
            raise ValueError(f"Account ID cannot be negative: {account_num}")
        
        if account_num > AccountIDValidator.MAX_ACCOUNT_ID:
            raise ValueError(f"Account ID exceeds maximum ({AccountIDValidator.MAX_ACCOUNT_ID}): {account_num}")
        
        return account_num
    
    @staticmethod
    def format_node_id(account_id: str) -> str:
        """
        Format account ID as a graph node ID.
        
        Args:
            account_id: Raw account ID
            
        Returns:
            Formatted node ID (e.g., "account_123")
        """
        validated_id = AccountIDValidator.validate(account_id)
        return f"account_{validated_id}"
    
    @staticmethod
    def extract_from_node_id(node_id: str) -> Optional[int]:
        """
        Extract account number from a node ID.
        
        Args:
            node_id: Node ID like "account_123"
            
        Returns:
            Account number or None if not a valid account node
        """
        if not node_id or not isinstance(node_id, str):
            return None
        
        # Extract number from "account_XXX" format
        match = re.match(r'account_(\d+)', node_id)
        if not match:
            return None
        
        try:
            return int(match.group(1))
        except ValueError:
            return None


class CaseIDValidator:
    """Validate case IDs."""
    
    # Case ID pattern: CASE_YYYYMMDD_NNN
    PATTERN = re.compile(r'^CASE_\d{8}_\d{1,5}$')
    
    @staticmethod
    def validate(case_id: str) -> str:
        """
        Validate a case ID format.
        
        Args:
            case_id: Case ID to validate
            
        Returns:
            Validated case ID
            
        Raises:
            ValueError: If case ID format is invalid
        """
        if not case_id:
            raise ValueError("Case ID cannot be empty")
        
        if not isinstance(case_id, str):
            raise ValueError(f"Case ID must be a string, got {type(case_id)}")
        
        # Check format
        if not CaseIDValidator.PATTERN.match(case_id):
            raise ValueError(
                f"Invalid case ID format: '{case_id}'. "
                f"Expected format: CASE_YYYYMMDD_NNN"
            )
        
        return case_id


class QueryValidator:
    """Validate and sanitize user queries."""
    
    MAX_QUERY_LENGTH = 1000
    MIN_QUERY_LENGTH = 3
    
    @staticmethod
    def validate(query: str) -> str:
        """
        Validate and sanitize a user query.
        
        Args:
            query: Raw query string
            
        Returns:
            Sanitized query
            
        Raises:
            ValueError: If query is invalid
        """
        if not query:
            raise ValueError("Query cannot be empty")
        
        if not isinstance(query, str):
            raise ValueError(f"Query must be a string, got {type(query)}")
        
        # Trim whitespace
        query = query.strip()
        
        # Length validation
        if len(query) < QueryValidator.MIN_QUERY_LENGTH:
            raise ValueError(
                f"Query too short (minimum {QueryValidator.MIN_QUERY_LENGTH} characters)"
            )
        
        if len(query) > QueryValidator.MAX_QUERY_LENGTH:
            raise ValueError(
                f"Query too long (maximum {QueryValidator.MAX_QUERY_LENGTH} characters)"
            )
        
        # Remove control characters and excessive whitespace
        query = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', query)
        query = re.sub(r'\s+', ' ', query)
        
        return query.strip()

