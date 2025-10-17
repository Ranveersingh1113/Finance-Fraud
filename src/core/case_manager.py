"""
Case Management System for Financial Intelligence Platform.
Provides persistent storage and management of investigation cases using SQLite.
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CaseManager:
    """
    Case management system with SQLite backend.
    
    Features:
    - Persistent case storage
    - Case status tracking
    - Query history per case
    - Analysis results storage
    - SAR generation and storage
    """
    
    def __init__(self, db_path: str = "./data/cases.db"):
        """
        Initialize case manager with SQLite database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        logger.info(f"CaseManager initialized with database: {db_path}")
    
    def _init_database(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Cases table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    analyst TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    tags TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Queries table (linked to cases)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS case_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    answer TEXT,
                    confidence_score REAL,
                    query_type TEXT,
                    processing_time REAL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (case_id) REFERENCES cases(case_id)
                )
            """)
            
            # Evidence table (linked to queries)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_id INTEGER NOT NULL,
                    case_id TEXT NOT NULL,
                    rank INTEGER,
                    score REAL,
                    document TEXT,
                    source TEXT,
                    metadata TEXT,
                    FOREIGN KEY (query_id) REFERENCES case_queries(id),
                    FOREIGN KEY (case_id) REFERENCES cases(case_id)
                )
            """)
            
            # SAR reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sar_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    report_content TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    analyst TEXT,
                    status TEXT DEFAULT 'draft',
                    FOREIGN KEY (case_id) REFERENCES cases(case_id)
                )
            """)
            
            conn.commit()
            logger.info("Database tables initialized successfully")
    
    def create_case(self, case_id: str, description: str, priority: str, 
                   analyst: str, tags: List[str] = None, metadata: Dict = None) -> Dict:
        """
        Create a new investigation case.
        
        Args:
            case_id: Unique case identifier
            description: Case description
            priority: Priority level (low, medium, high, critical)
            analyst: Analyst name
            tags: List of tags
            metadata: Additional metadata
            
        Returns:
            Case data dictionary
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.now().isoformat()
                tags_json = json.dumps(tags) if tags else json.dumps([])
                metadata_json = json.dumps(metadata) if metadata else json.dumps({})
                
                cursor.execute("""
                    INSERT INTO cases (case_id, description, priority, analyst, 
                                     tags, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (case_id, description, priority, analyst, tags_json, now, now, metadata_json))
                
                conn.commit()
                
                logger.info(f"Case {case_id} created successfully")
                
                return {
                    'case_id': case_id,
                    'description': description,
                    'priority': priority,
                    'analyst': analyst,
                    'status': 'active',
                    'tags': tags or [],
                    'created_at': now,
                    'updated_at': now,
                    'metadata': metadata or {}
                }
                
        except sqlite3.IntegrityError:
            logger.error(f"Case {case_id} already exists")
            raise ValueError(f"Case {case_id} already exists")
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            raise
    
    def get_case(self, case_id: str) -> Optional[Dict]:
        """
        Get case details by ID.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Case data dictionary or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT case_id, description, priority, analyst, status, 
                           tags, created_at, updated_at, metadata
                    FROM cases WHERE case_id = ?
                """, (case_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'case_id': row[0],
                        'description': row[1],
                        'priority': row[2],
                        'analyst': row[3],
                        'status': row[4],
                        'tags': json.loads(row[5]) if row[5] else [],
                        'created_at': row[6],
                        'updated_at': row[7],
                        'metadata': json.loads(row[8]) if row[8] else {}
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting case: {e}")
            return None
    
    def list_cases(self, status: str = None) -> List[Dict]:
        """
        List all cases, optionally filtered by status.
        
        Args:
            status: Filter by status (active, closed, etc.)
            
        Returns:
            List of case dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if status:
                    cursor.execute("""
                        SELECT case_id, description, priority, analyst, status, 
                               tags, created_at, updated_at
                        FROM cases WHERE status = ?
                        ORDER BY created_at DESC
                    """, (status,))
                else:
                    cursor.execute("""
                        SELECT case_id, description, priority, analyst, status, 
                               tags, created_at, updated_at
                        FROM cases
                        ORDER BY created_at DESC
                    """)
                
                cases = []
                for row in cursor.fetchall():
                    cases.append({
                        'case_id': row[0],
                        'description': row[1],
                        'priority': row[2],
                        'analyst': row[3],
                        'status': row[4],
                        'tags': json.loads(row[5]) if row[5] else [],
                        'created_at': row[6],
                        'updated_at': row[7]
                    })
                
                return cases
                
        except Exception as e:
            logger.error(f"Error listing cases: {e}")
            return []
    
    def update_case_status(self, case_id: str, status: str) -> bool:
        """
        Update case status.
        
        Args:
            case_id: Case identifier
            status: New status
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE cases 
                    SET status = ?, updated_at = ?
                    WHERE case_id = ?
                """, (status, datetime.now().isoformat(), case_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating case status: {e}")
            return False
    
    def add_query_to_case(self, case_id: str, query: str, answer: str, 
                         confidence_score: float, query_type: str, 
                         processing_time: float, evidence: List[Dict] = None) -> int:
        """
        Add a query and its results to a case.
        
        Args:
            case_id: Case identifier
            query: Query text
            answer: Generated answer
            confidence_score: Confidence score
            query_type: Type of query
            processing_time: Processing time in seconds
            evidence: List of evidence documents
            
        Returns:
            Query ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert query
                cursor.execute("""
                    INSERT INTO case_queries 
                    (case_id, query, answer, confidence_score, query_type, 
                     processing_time, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (case_id, query, answer, confidence_score, query_type, 
                      processing_time, datetime.now().isoformat()))
                
                query_id = cursor.lastrowid
                
                # Insert evidence
                if evidence:
                    for ev in evidence:
                        cursor.execute("""
                            INSERT INTO query_evidence 
                            (query_id, case_id, rank, score, document, source, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (query_id, case_id, ev.get('rank'), ev.get('score'),
                              ev.get('document'), ev.get('source'), 
                              json.dumps(ev.get('metadata', {}))))
                
                # Update case timestamp
                cursor.execute("""
                    UPDATE cases SET updated_at = ? WHERE case_id = ?
                """, (datetime.now().isoformat(), case_id))
                
                conn.commit()
                logger.info(f"Query added to case {case_id}")
                
                return query_id
                
        except Exception as e:
            logger.error(f"Error adding query to case: {e}")
            raise
    
    def get_case_queries(self, case_id: str) -> List[Dict]:
        """
        Get all queries for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of query dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, query, answer, confidence_score, query_type, 
                           processing_time, timestamp
                    FROM case_queries
                    WHERE case_id = ?
                    ORDER BY timestamp DESC
                """, (case_id,))
                
                queries = []
                for row in cursor.fetchall():
                    queries.append({
                        'id': row[0],
                        'query': row[1],
                        'answer': row[2],
                        'confidence_score': row[3],
                        'query_type': row[4],
                        'processing_time': row[5],
                        'timestamp': row[6]
                    })
                
                return queries
                
        except Exception as e:
            logger.error(f"Error getting case queries: {e}")
            return []
    
    def save_sar_report(self, case_id: str, report_content: str, 
                       analyst: str, status: str = 'draft') -> int:
        """
        Save a SAR report for a case.
        
        Args:
            case_id: Case identifier
            report_content: Report content
            analyst: Analyst name
            status: Report status (draft, final, submitted)
            
        Returns:
            Report ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO sar_reports 
                    (case_id, report_content, generated_at, analyst, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (case_id, report_content, datetime.now().isoformat(), 
                      analyst, status))
                
                report_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"SAR report saved for case {case_id}")
                return report_id
                
        except Exception as e:
            logger.error(f"Error saving SAR report: {e}")
            raise
    
    def get_sar_reports(self, case_id: str) -> List[Dict]:
        """
        Get all SAR reports for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of SAR report dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, report_content, generated_at, analyst, status
                    FROM sar_reports
                    WHERE case_id = ?
                    ORDER BY generated_at DESC
                """, (case_id,))
                
                reports = []
                for row in cursor.fetchall():
                    reports.append({
                        'id': row[0],
                        'report_content': row[1],
                        'generated_at': row[2],
                        'analyst': row[3],
                        'status': row[4]
                    })
                
                return reports
                
        except Exception as e:
            logger.error(f"Error getting SAR reports: {e}")
            return []
    
    def delete_case(self, case_id: str) -> bool:
        """
        Delete a case and all associated data.
        
        Args:
            case_id: Case identifier
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete in order due to foreign key constraints
                cursor.execute("DELETE FROM query_evidence WHERE case_id = ?", (case_id,))
                cursor.execute("DELETE FROM case_queries WHERE case_id = ?", (case_id,))
                cursor.execute("DELETE FROM sar_reports WHERE case_id = ?", (case_id,))
                cursor.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
                
                conn.commit()
                logger.info(f"Case {case_id} deleted successfully")
                
                return True
                
        except Exception as e:
            logger.error(f"Error deleting case: {e}")
            return False
    
    def get_case_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about cases.
        
        Returns:
            Dictionary with statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total cases
                cursor.execute("SELECT COUNT(*) FROM cases")
                total_cases = cursor.fetchone()[0]
                
                # Active cases
                cursor.execute("SELECT COUNT(*) FROM cases WHERE status = 'active'")
                active_cases = cursor.fetchone()[0]
                
                # Total queries
                cursor.execute("SELECT COUNT(*) FROM case_queries")
                total_queries = cursor.fetchone()[0]
                
                # Cases by priority
                cursor.execute("""
                    SELECT priority, COUNT(*) 
                    FROM cases 
                    GROUP BY priority
                """)
                priority_breakdown = dict(cursor.fetchall())
                
                # Average queries per case
                avg_queries = total_queries / total_cases if total_cases > 0 else 0
                
                return {
                    'total_cases': total_cases,
                    'active_cases': active_cases,
                    'closed_cases': total_cases - active_cases,
                    'total_queries': total_queries,
                    'average_queries_per_case': avg_queries,
                    'priority_breakdown': priority_breakdown
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

