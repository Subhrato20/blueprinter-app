"""Local storage implementation for plans using SQLite."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import structlog

logger = structlog.get_logger(__name__)

# Database file path
DB_PATH = Path.home() / ".blueprinter" / "plans.db"


class LocalPlanStorage:
    """Local SQLite storage for development plans."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plans (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    plan_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plan_messages (
                    id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL,
                    user_question TEXT NOT NULL,
                    node_path TEXT,
                    selection_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plan_id) REFERENCES plans (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plan_revisions (
                    id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL,
                    message_id TEXT,
                    patch_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plan_id) REFERENCES plans (id)
                )
            """)
            
            conn.commit()
            logger.info("Local database initialized", db_path=str(self.db_path))
    
    async def create_plan(self, project_id: str, user_id: str, plan_json: Dict[str, Any]) -> str:
        """Create a new plan and return its ID."""
        plan_id = str(uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO plans (id, project_id, user_id, plan_json) VALUES (?, ?, ?, ?)",
                (plan_id, project_id, user_id, json.dumps(plan_json))
            )
            conn.commit()
        
        logger.info("Plan created in local storage", plan_id=plan_id, project_id=project_id)
        return plan_id
    
    async def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get a plan by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM plans WHERE id = ?",
                (plan_id,)
            )
            row = cursor.fetchone()
            
            if row:
                plan_data = {
                    "id": row["id"],
                    "project_id": row["project_id"],
                    "user_id": row["user_id"],
                    "plan_json": json.loads(row["plan_json"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                logger.info("Plan retrieved from local storage", plan_id=plan_id)
                return plan_data
            
            logger.warning("Plan not found in local storage", plan_id=plan_id)
            return None
    
    async def update_plan(self, plan_id: str, plan_json: Dict[str, Any]) -> bool:
        """Update an existing plan."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE plans SET plan_json = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (json.dumps(plan_json), plan_id)
            )
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info("Plan updated in local storage", plan_id=plan_id)
                return True
            else:
                logger.warning("Plan not found for update", plan_id=plan_id)
                return False
    
    async def list_plans(self, project_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List plans with optional filtering."""
        query = "SELECT * FROM plans WHERE 1=1"
        params = []
        
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        query += " ORDER BY created_at DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            plans = []
            for row in rows:
                plan_data = {
                    "id": row["id"],
                    "project_id": row["project_id"],
                    "user_id": row["user_id"],
                    "plan_json": json.loads(row["plan_json"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                plans.append(plan_data)
            
            logger.info("Plans listed from local storage", count=len(plans))
            return plans
    
    async def create_plan_message(self, plan_id: str, user_question: str, node_path: str, selection_text: str) -> str:
        """Create a plan message and return its ID."""
        message_id = str(uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO plan_messages (id, plan_id, user_question, node_path, selection_text) VALUES (?, ?, ?, ?, ?)",
                (message_id, plan_id, user_question, node_path, selection_text)
            )
            conn.commit()
        
        logger.info("Plan message created in local storage", message_id=message_id, plan_id=plan_id)
        return message_id
    
    async def create_plan_revision(self, plan_id: str, message_id: str, patch: List[Dict[str, Any]]) -> str:
        """Create a plan revision and return its ID."""
        revision_id = str(uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO plan_revisions (id, plan_id, message_id, patch_json) VALUES (?, ?, ?, ?)",
                (revision_id, plan_id, message_id, json.dumps(patch))
            )
            conn.commit()
        
        logger.info("Plan revision created in local storage", revision_id=revision_id, plan_id=plan_id)
        return revision_id
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the local database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) as plan_count FROM plans")
            plan_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) as message_count FROM plan_messages")
            message_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) as revision_count FROM plan_revisions")
            revision_count = cursor.fetchone()[0]
        
        return {
            "database_path": str(self.db_path),
            "plan_count": plan_count,
            "message_count": message_count,
            "revision_count": revision_count,
            "database_size": self.db_path.stat().st_size if self.db_path.exists() else 0
        }


# Global instance
local_storage = LocalPlanStorage()
