# src/storage/models.py
"""Database models for storing review data"""

import sqlite3
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from src.utils.config import Config

@dataclass
class ReviewSession:
    """A complete review session"""
    id: Optional[int] = None
    document_filename: str = ""
    document_path: str = ""
    user_id: str = ""
    created_at: Optional[datetime] = None
    processing_method: str = ""
    total_processing_time: float = 0.0
    status: str = "pending"  # pending, processing, completed, failed

@dataclass
class AgentFinding:
    """A single finding from an agent"""
    id: Optional[int] = None
    session_id: int = 0
    agent_name: str = ""
    severity: str = ""  # error, warning, info
    category: str = ""  # formatting, technical, brand, etc.
    description: str = ""
    location: str = ""  # Page X, Section Y, etc.
    suggestion: Optional[str] = None
    confidence: float = 0.0
    created_at: Optional[datetime] = None

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (Config.DATA_DIR / "reviews.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS review_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_filename TEXT NOT NULL,
                    document_path TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processing_method TEXT NOT NULL,
                    total_processing_time REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    agent_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    location TEXT NOT NULL,
                    suggestion TEXT,
                    confidence REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES review_sessions (id)
                )
            """)
            
            conn.commit()
    
    def create_review_session(self, session: ReviewSession) -> int:
        """Create a new review session and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO review_sessions 
                (document_filename, document_path, user_id, processing_method, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session.document_filename,
                session.document_path,
                session.user_id,
                session.processing_method,
                session.status
            ))
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to insert review session, no row ID returned.")
            return cursor.lastrowid
    
    def add_agent_finding(self, finding: AgentFinding) -> int:
        """Add an agent finding and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO agent_findings 
                (session_id, agent_name, severity, category, description, location, suggestion, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                finding.session_id,
                finding.agent_name,
                finding.severity,
                finding.category,
                finding.description,
                finding.location,
                finding.suggestion,
                finding.confidence
            ))
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to insert agent finding, no row ID returned.")
            return cursor.lastrowid

    def get_session_findings(self, session_id: int) -> List[AgentFinding]:
        """Get all findings for a session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM agent_findings WHERE session_id = ? 
                ORDER BY created_at
            """, (session_id,)).fetchall()
            
            return [AgentFinding(**dict(row)) for row in rows]
    
    def update_session_status(self, session_id: int, status: str, processing_time: float = 0.0):
        """Update session status and processing time"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE review_sessions 
                SET status = ?, total_processing_time = ?
                WHERE id = ?
            """, (status, processing_time, session_id))
            conn.commit()
    
    def get_recent_sessions(self, user_id: str, limit: int = 10) -> List[ReviewSession]:
        """Get recent review sessions for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM review_sessions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit)).fetchall()
            
            return [ReviewSession(**dict(row)) for row in rows]
    
    def get_session_by_id(self, session_id: int) -> Optional[ReviewSession]:
        """Get a specific review session by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT * FROM review_sessions WHERE id = ?
            """, (session_id,)).fetchone()
            
            return ReviewSession(**dict(row)) if row else None
    
    def update_session_processing_method(self, session_id: int, processing_method: str):
        """Update the processing method for a session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE review_sessions 
                SET processing_method = ?
                WHERE id = ?
            """, (processing_method, session_id))
            conn.commit()