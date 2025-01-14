import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class StateManager:
    """Manages persistent state for the CLI application."""
    
    def __init__(self, state_file: str = ".cli_state.json"):
        """Initialize the state manager with a state file path."""
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load state from file or create default state."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._create_default_state()
        return self._create_default_state()
    
    def _create_default_state(self) -> Dict:
        """Create a default state structure."""
        return {
            'chat_history': [],
            'topics': [],
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_state(self):
        """Save current state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def add_message(self, role: str, content: str):
        """Add a message to the chat history."""
        self.state['chat_history'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        self._save_state()
    
    def add_topics(self, topics: List[str]):
        """Store found topics."""
        self.state['topics'] = topics
        self.state['last_updated'] = datetime.now().isoformat()
        self._save_state()
    
    def get_chat_history(self) -> List[Dict]:
        """Get the full chat history."""
        return self.state['chat_history']
    
    def get_topics(self) -> List[str]:
        """Get stored topics."""
        return self.state['topics']
    
    def get_last_topics_update(self) -> Optional[str]:
        """Get when topics were last updated."""
        return self.state.get('last_updated')
    
    def clear_history(self):
        """Clear the chat history."""
        self.state['chat_history'] = []
        self._save_state()
