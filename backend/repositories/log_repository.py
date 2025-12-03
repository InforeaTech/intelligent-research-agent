"""
Log repository for caching and audit trail.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.log import Log
from repositories.base import BaseRepository


class LogRepository(BaseRepository[Log]):
    """Repository for Log model with caching functionality."""
    
    def __init__(self, db: Session):
        """
        Initialize Log repository.
        
        Args:
            db: Database session
        """
        super().__init__(Log, db)

    def check_cache(
        self, 
        action_type: str, 
        search_data: Optional[Dict] = None, 
        user_input: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Check for cached results based on action type and input data.
        
        Fetches all logs of the given action_type and compares JSON in Python
        since SQL-level JSON comparison is unreliable across databases.
        
        Args:
            action_type: Type of action ('search_query', 'generate_profile', etc.)
            search_data: Search criteria as dictionary (optional)
            user_input: User input parameters as dictionary (optional)
            
        Returns:
            Cached final_output string or None if no cache hit
        """
        # Get all logs of this action type
        logs = self.db.query(Log).filter(
            Log.action_type == action_type
        ).order_by(desc(Log.timestamp)).limit(50).all() # Limit to recent 50 for performance
        
        # Search JSON should be defined as canonicalized strings for comparison
        search_json = json.dumps(search_data, sort_keys=True) if search_data else None
        input_json = json.dumps(user_input, sort_keys=True) if user_input else None
        
        # Find matching log by comparing JSON in Python
        for log in logs:
            # Skip error results
            if log.final_output and (log.final_output.startswith("Error:") or log.final_output.startswith("Error ")):
                continue
            
            # Check if this log matches our criteria
            matches = True
            
            # Compare search_data if provided
            if search_data is not None:
                log_search_json = log.search_data if isinstance(log.search_data, str) else json.dumps(log.search_data, sort_keys=True) if log.search_data else None
                if log_search_json != search_json:
                    matches = False
            
            # Compare user_input if provided
            if user_input is not None:
                log_input_json = log.user_input if isinstance(log.user_input, str) else json.dumps(log.user_input, sort_keys=True) if log.user_input else None
                if log_input_json != input_json:
                    matches = False
            
            # Return first match (most recent due to ordering)
            if matches and log.final_output:
                return log.final_output
        
        return None

    def check_cache_fuzzy(
        self,
        action_type: str,
        user_input: Optional[Dict] = None,
        similarity_threshold: float = 0.8
    ) -> Optional[str]:
        """
        Check for cached results using fuzzy matching on text fields.
        """
        import difflib
        
        # Fetch recent logs
        logs = self.db.query(Log).filter(
            Log.action_type == action_type
        ).order_by(desc(Log.timestamp)).limit(20).all()
        
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

        for log in logs:
            # Skip error results
            if log.final_output and (log.final_output.startswith("Error:") or log.final_output.startswith("Error ")):
                continue

            # Parse log user_input
            log_input = log.user_input
            if isinstance(log_input, str):
                try:
                    log_input = json.loads(log_input)
                except:
                    log_input = {}
            if not log_input:
                log_input = {}
            
            # Extract comparison text from row
            row_text = ""
            if action_type == "deep_research" or action_type == "deep_research_planning":
                row_text = log_input.get("topic", "")
            elif action_type == "generate_note":
                row_text = log_input.get("profile_text", "")
            
            if not row_text:
                continue

            # Calculate similarity
            similarity = difflib.SequenceMatcher(None, target_text, row_text).ratio()
            if similarity >= similarity_threshold:
                # For notes, also check if tone, length, and context match
                if action_type == "generate_note":
                    if (log_input.get("tone") == user_input.get("tone") and 
                        log_input.get("length") == user_input.get("length") and
                        log_input.get("context") == user_input.get("context")):
                        return log.final_output
                else:
                    return log.final_output

        return None

    def get_recent_note_for_profile(self, profile_text: str, similarity_threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """Retrieves the most recent note generated for a similar profile."""
        import difflib
        
        # Fetch recent note generation logs
        logs = self.db.query(Log).filter(
            Log.action_type == 'generate_note'
        ).order_by(desc(Log.timestamp)).limit(20).all()
        
        if not profile_text:
            return None
        
        for log in logs:
            # Skip error results
            if log.final_output and (log.final_output.startswith("Error:") or log.final_output.startswith("Error ")):
                continue

            log_input = log.user_input
            if isinstance(log_input, str):
                try:
                    log_input = json.loads(log_input)
                except:
                    log_input = {}
            if not log_input:
                log_input = {}

            row_profile = log_input.get('profile_text', '')
            
            if not row_profile:
                continue
            
            # Calculate similarity
            similarity = difflib.SequenceMatcher(None, profile_text, row_profile).ratio()
            if similarity >= similarity_threshold:
                return {
                    'note': log.final_output,
                    'tone': log_input.get('tone', 'professional'),
                    'length': log_input.get('length', 300),
                    'context': log_input.get('context', '')
                }
        
        return None

    def create_log(
        self, 
        action_type: str, 
        user_id: Optional[int] = None, 
        user_input: Optional[Dict] = None,
        search_data: Optional[Dict] = None,
        model_input: Optional[str] = None,
        model_output: Optional[str] = None,
        final_output: Optional[str] = None
    ) -> Log:
        """
        Create a new log entry.
        
        Handles JSON serialization of dict fields automatically.
        
        Args:
            action_type: Type of action being logged
            user_id: User's ID (optional, for anonymous actions)
            user_input: User input parameters as dict
            search_data: Search criteria as dict
            model_input: Prompt sent to LLM
            model_output: Raw LLM response
            final_output: Processed final output
            
        Returns:
            Created Log instance
        """
        # Serialize JSON fields
        user_input_json = json.dumps(user_input, sort_keys=True) if user_input else None
        search_data_json = json.dumps(search_data, sort_keys=True) if search_data else None
        
        return self.create(
            action_type=action_type,
            user_id=user_id,
            user_input=user_input_json,
            search_data=search_data_json,
            model_input=model_input,
            model_output=model_output,
            final_output=final_output
        )

    def get_by_user(
        self, 
        user_id: int, 
        action_type: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Log]:
        """
        Get logs for a specific user with optional filtering.
        
        Args:
            user_id: User's ID
            action_type: Optional filter by action type
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Log instances
        """
        query = self.db.query(Log).filter(Log.user_id == user_id)
        
        if action_type:
            query = query.filter(Log.action_type == action_type)
        
        return query.order_by(desc(Log.timestamp)).offset(skip).limit(limit).all()

    def get_recent(
        self, 
        action_type: Optional[str] = None, 
        limit: int = 100
    ) -> List[Log]:
        """
        Get recent logs, optionally filtered by action type.
        
        Args:
            action_type: Optional filter by action type
            limit: Maximum number of records to return
            
        Returns:
            List of recent Log instances
        """
        query = self.db.query(Log)
        
        if action_type:
            query = query.filter(Log.action_type == action_type)
        
        return query.order_by(desc(Log.timestamp)).limit(limit).all()

    def clear_cache(self, action_type: Optional[str] = None) -> int:
        """
        Clear cached logs.
        
        Args:
            action_type: Optional - only clear logs of this type
            
        Returns:
            Number of logs deleted
        """
        query = self.db.query(Log)
        
        if action_type:
            query = query.filter(Log.action_type == action_type)
        
        count = query.count()
        query.delete()
        self.db.commit()
        
        return count
