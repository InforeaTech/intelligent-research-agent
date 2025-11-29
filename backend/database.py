import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import difflib
from logger_config import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "agent_logs.db"):
        # Ensure db is in the same directory as this file if relative path
        if not os.path.isabs(db_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(current_dir, db_path)
        else:
            self.db_path = db_path
            
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT NOT NULL,
                user_input JSON,
                search_data JSON,
                model_input TEXT,
                model_output TEXT,
                final_output TEXT
            )
        ''')
        
        # Create index for performance optimization
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_action_timestamp 
            ON logs(action_type, timestamp DESC)
        ''')
        
        conn.commit()
        conn.close()

    def log_interaction(self, 
                        action_type: str, 
                        user_input: Optional[Dict[str, Any]] = None,
                        search_data: Optional[Any] = None,
                        model_input: Optional[str] = None,
                        model_output: Optional[str] = None,
                        final_output: Optional[str] = None):
        """Logs an interaction to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Serialize JSON fields
        user_input_json = json.dumps(user_input) if user_input else None
        search_data_json = json.dumps(search_data) if search_data else None
        
        cursor.execute('''
            INSERT INTO logs (
                timestamp, action_type, user_input, search_data, 
                model_input, model_output, final_output
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow(),
            action_type,
            user_input_json,
            search_data_json,
            model_input,
            model_output,
            final_output
        ))
        
        conn.commit()
        conn.close()
        logger.info("Logged interaction", extra={'extra_data': {'action_type': action_type}})

    def get_logs(self, limit: int = 10):
        """Retrieve recent logs."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        
        logs = []
        for row in rows:
            logs.append(dict(row))
            
        conn.close()
        return logs

    def check_existing_log(self, action_type: str, user_input: Optional[Dict[str, Any]] = None, search_data: Optional[Any] = None, bypass_cache: bool = False, similarity_threshold: float = 0.8) -> Optional[str]:
        """Checks if a log entry exists with the same inputs (fuzzy match) and returns the final output."""
        if bypass_cache:
            logger.debug("Cache bypass", extra={'extra_data': {'action_type': action_type}})
            return None

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # For exact match optimization (e.g. search_data present), try exact first
        if search_data:
            search_data_json = json.dumps(search_data)
            query = 'SELECT final_output FROM logs WHERE action_type = ? AND search_data = ? ORDER BY timestamp DESC LIMIT 1'
            cursor.execute(query, (action_type, search_data_json))
            row = cursor.fetchone()
            if row:
                # Check if cached result is an error message
                cached_output = row['final_output']
                if cached_output and (cached_output.startswith("Error:") or cached_output.startswith("Error ")):
                    logger.info("Skipping cached error", extra={'extra_data': {'action_type': action_type, 'error_preview': cached_output[:50]}})
                    conn.close()
                    return None
                logger.info("Cache hit (Exact)", extra={'extra_data': {'action_type': action_type}})
                conn.close()
                return cached_output
        
        # For fuzzy match, we fetch recent logs and compare in Python
        # We limit to 20 recent logs to avoid performance issues
        cursor.execute('SELECT user_input, final_output FROM logs WHERE action_type = ? ORDER BY timestamp DESC LIMIT 20', (action_type,))
        rows = cursor.fetchall()
        conn.close()

        if not user_input:
            return None

        # Determine the text field to compare based on action_type
        target_text = ""
        if action_type == "deep_research" or action_type == "deep_research_planning":
            target_text = user_input.get("topic", "")
        elif action_type == "generate_note":
            target_text = user_input.get("profile_text", "")
        
        if not target_text:
            return None

        for row in rows:
            row_input = json.loads(row['user_input']) if row['user_input'] else {}
            
            # Extract comparison text from row
            row_text = ""
            if action_type == "deep_research" or action_type == "deep_research_planning":
                row_text = row_input.get("topic", "")
            elif action_type == "generate_note":
                row_text = row_input.get("profile_text", "")
            
            if not row_text:
                continue

            # Calculate similarity
            similarity = difflib.SequenceMatcher(None, target_text, row_text).ratio()
            if similarity >= similarity_threshold:
                # For notes, also check if tone, length, and context match
                if action_type == "generate_note":
                    if (row_input.get("tone") == user_input.get("tone") and 
                        row_input.get("length") == user_input.get("length") and
                        row_input.get("context") == user_input.get("context")):
                        # Check if cached result is an error message
                        cached_output = row['final_output']
                        if cached_output and (cached_output.startswith("Error:") or cached_output.startswith("Error ")):
                            logger.info("Skipping cached error", extra={'extra_data': {'action_type': action_type, 'error_preview': cached_output[:50]}})
                            continue
                        logger.info("Cache hit (Fuzzy) with matching context", extra={'extra_data': {'action_type': action_type, 'similarity': round(similarity, 2)}})
                        return cached_output
                else:
                    # Check if cached result is an error message
                    cached_output = row['final_output']
                    if cached_output and (cached_output.startswith("Error:") or cached_output.startswith("Error ")):
                        logger.info("Skipping cached error", extra={'extra_data': {'action_type': action_type, 'error_preview': cached_output[:50]}})
                        continue
                    logger.info("Cache hit (Fuzzy)", extra={'extra_data': {'action_type': action_type, 'similarity': round(similarity, 2)}})
                    return cached_output

        return None

    def get_recent_note_for_profile(self, profile_text: str, similarity_threshold: float = 0.8) -> Optional[Dict[str, str]]:
        """Retrieves the most recent note generated for a similar profile."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Fetch recent note generation logs
        cursor.execute('SELECT user_input, final_output FROM logs WHERE action_type = ? ORDER BY timestamp DESC LIMIT 20', ('generate_note',))
        rows = cursor.fetchall()
        conn.close()
        
        if not profile_text:
            return None
        
        for row in rows:
            row_input = json.loads(row['user_input']) if row['user_input'] else {}
            row_profile = row_input.get('profile_text', '')
            
            if not row_profile:
                continue
            
            # Calculate similarity
            similarity = difflib.SequenceMatcher(None, profile_text, row_profile).ratio()
            if similarity >= similarity_threshold:
                logger.info("Found cached note", extra={'extra_data': {'similarity': round(similarity, 2)}})
                return {
                    'note': row['final_output'],
                    'tone': row_input.get('tone', 'professional'),
                    'length': row_input.get('length', 300),
                    'context': row_input.get('context', '')
                }
        
        return None

