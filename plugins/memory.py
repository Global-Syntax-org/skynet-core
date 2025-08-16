"""
Chat memory management for Skynet Lite
Handles conversation history and context tracking
"""

from typing import List, Dict, Optional
from datetime import datetime
import json


class ChatMemoryManager:
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversation_history: List[Dict] = []
        self.session_start = datetime.now()
    
    def add_user_message(self, message: str, timestamp: Optional[datetime] = None):
        """Add a user message to the conversation history"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": timestamp.isoformat()
        })
        
        self._trim_history()
    
    def add_assistant_message(self, message: str, timestamp: Optional[datetime] = None):
        """Add an assistant message to the conversation history"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.conversation_history.append({
            "role": "assistant",
            "content": message,
            "timestamp": timestamp.isoformat()
        })
        
        self._trim_history()
    
    def get_conversation_history(self, format_type: str = "text") -> str:
        """
        Get the conversation history in the specified format
        
        Args:
            format_type: 'text' for human-readable format, 'json' for structured data
        
        Returns:
            Formatted conversation history
        """
        if format_type == "json":
            return json.dumps(self.conversation_history, indent=2)
        
        # Text format
        if not self.conversation_history:
            return "No conversation history yet."
        
        formatted_history = []
        for entry in self.conversation_history:
            role = "You" if entry["role"] == "user" else "Skynet"
            formatted_history.append(f"{role}: {entry['content']}")
        
        return "\n".join(formatted_history)
    
    def get_recent_context(self, num_messages: int = 4) -> List[Dict]:
        """Get the most recent messages for context"""
        return self.conversation_history[-num_messages:] if self.conversation_history else []
    
    def get_last_user_message(self) -> Optional[str]:
        """Get the last message from the user"""
        for entry in reversed(self.conversation_history):
            if entry["role"] == "user":
                return entry["content"]
        return None
    
    def get_last_assistant_message(self) -> Optional[str]:
        """Get the last message from the assistant"""
        for entry in reversed(self.conversation_history):
            if entry["role"] == "assistant":
                return entry["content"]
        return None
    
    def clear_history(self):
        """Clear all conversation history"""
        self.conversation_history.clear()
        self.session_start = datetime.now()
    
    def save_to_file(self, filename: str):
        """Save conversation history to a JSON file"""
        try:
            session_data = {
                "session_start": self.session_start.isoformat(),
                "conversation_history": self.conversation_history,
                "total_messages": len(self.conversation_history)
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Conversation saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")
    
    def load_from_file(self, filename: str) -> bool:
        """Load conversation history from a JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.conversation_history = session_data.get("conversation_history", [])
            
            # Parse session start time
            session_start_str = session_data.get("session_start")
            if session_start_str:
                self.session_start = datetime.fromisoformat(session_start_str)
            
            print(f"📂 Conversation loaded from {filename}")
            print(f"   Total messages: {len(self.conversation_history)}")
            return True
            
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            return False
        except Exception as e:
            print(f"❌ Error loading conversation: {e}")
            return False
    
    def get_session_stats(self) -> Dict:
        """Get statistics about the current session"""
        user_messages = sum(1 for entry in self.conversation_history if entry["role"] == "user")
        assistant_messages = sum(1 for entry in self.conversation_history if entry["role"] == "assistant")
        
        session_duration = datetime.now() - self.session_start
        
        return {
            "session_start": self.session_start.isoformat(),
            "session_duration_minutes": session_duration.total_seconds() / 60,
            "total_messages": len(self.conversation_history),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages
        }
    
    def _trim_history(self):
        """Keep only the most recent messages up to max_history"""
        # If max_history is falsy (0 or None) treat as unlimited
        if not self.max_history:
            return

        if len(self.conversation_history) > self.max_history:
            # Remove oldest messages, but try to keep pairs of user/assistant messages
            excess = len(self.conversation_history) - self.max_history
            self.conversation_history = self.conversation_history[excess:]
    
    def search_history(self, query: str, case_sensitive: bool = False) -> List[Dict]:
        """
        Search through conversation history for messages containing the query
        
        Args:
            query: Text to search for
            case_sensitive: Whether search should be case sensitive
        
        Returns:
            List of matching conversation entries
        """
        if not case_sensitive:
            query = query.lower()
        
        matches = []
        for entry in self.conversation_history:
            content = entry["content"]
            if not case_sensitive:
                content = content.lower()
            
            if query in content:
                matches.append(entry)
        
        return matches
