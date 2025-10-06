"""
User Action Logger for SpokyAI
Tracks and logs user interactions with the system
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# File handler for action logs
action_log_file = LOGS_DIR / f"user_actions_{datetime.now().strftime('%Y%m%d')}.log"
file_handler = logging.FileHandler(action_log_file)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class UserActionLogger:
    """Logger for user actions and interactions"""
    
    def __init__(self, user_id: str = "default_user"):
        """
        Initialize user action logger
        
        Args:
            user_id: Identifier for the user
        """
        self.user_id = user_id
        self.session_start = datetime.utcnow()
        self.action_count = 0
        
        logger.info(f"User action logger initialized for user: {user_id}")
        self.log_action("session_start", {"session_start_time": self.session_start.isoformat()})
    
    def log_action(
        self,
        action_type: str,
        details: Optional[Dict[str, Any]] = None,
        status: str = "completed"
    ):
        """
        Log a user action
        
        Args:
            action_type: Type of action (e.g., 'click', 'voice_command', 'keyboard_input')
            details: Additional details about the action
            status: Status of the action ('completed', 'failed', 'in_progress')
        """
        self.action_count += 1
        
        log_entry = {
            "user_id": self.user_id,
            "action_id": self.action_count,
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": action_type,
            "details": details or {},
            "status": status
        }
        
        logger.info(f"USER_ACTION: {json.dumps(log_entry)}")
    
    def log_mouse_click(self, x: int, y: int, button: str = "left"):
        """Log a mouse click action"""
        self.log_action(
            "mouse_click",
            {
                "x": x,
                "y": y,
                "button": button
            }
        )
    
    def log_keyboard_input(self, keys: str, context: Optional[str] = None):
        """Log keyboard input"""
        self.log_action(
            "keyboard_input",
            {
                "keys": keys,
                "context": context
            }
        )
    
    def log_voice_command(self, command: str, recognized_text: str, confidence: float = 0.0):
        """Log a voice command"""
        self.log_action(
            "voice_command",
            {
                "command": command,
                "recognized_text": recognized_text,
                "confidence": confidence
            }
        )
    
    def log_window_switch(self, from_window: str, to_window: str):
        """Log window/application switch"""
        self.log_action(
            "window_switch",
            {
                "from": from_window,
                "to": to_window
            }
        )
    
    def log_file_operation(self, operation: str, file_path: str, status: str = "completed"):
        """Log file operations (open, save, delete, etc.)"""
        self.log_action(
            "file_operation",
            {
                "operation": operation,
                "file_path": file_path
            },
            status=status
        )
    
    def log_automation_task(self, task_name: str, duration: float, status: str = "completed"):
        """Log automated task execution"""
        self.log_action(
            "automation_task",
            {
                "task_name": task_name,
                "duration_seconds": duration
            },
            status=status
        )
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict] = None):
        """Log an error"""
        self.log_action(
            "error",
            {
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {}
            },
            status="failed"
        )
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for the current session"""
        session_duration = (datetime.utcnow() - self.session_start).total_seconds()
        
        stats = {
            "user_id": self.user_id,
            "session_start": self.session_start.isoformat(),
            "session_duration_seconds": session_duration,
            "total_actions": self.action_count
        }
        
        return stats
    
    def end_session(self):
        """End the logging session"""
        stats = self.get_session_stats()
        self.log_action("session_end", stats)
        logger.info(f"User session ended. Stats: {json.dumps(stats)}")


# Global logger instance
_default_logger: Optional[UserActionLogger] = None


def get_logger(user_id: str = "default_user") -> UserActionLogger:
    """
    Get or create a user action logger instance
    
    Args:
        user_id: User identifier
    
    Returns:
        UserActionLogger instance
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = UserActionLogger(user_id)
    return _default_logger


def log_action(action_type: str, details: Optional[Dict[str, Any]] = None, status: str = "completed"):
    """
    Convenience function to log an action using the default logger
    
    Args:
        action_type: Type of action
        details: Action details
        status: Action status
    """
    logger_instance = get_logger()
    logger_instance.log_action(action_type, details, status)


# Example usage
if __name__ == "__main__":
    # Create a logger for a user
    user_logger = UserActionLogger("user_123")
    
    # Log various actions
    user_logger.log_mouse_click(100, 200, "left")
    user_logger.log_keyboard_input("Hello SpokyAI", "text_editor")
    user_logger.log_voice_command("open browser", "open browser", 0.95)
    user_logger.log_window_switch("Terminal", "Chrome")
    user_logger.log_file_operation("open", "/home/user/document.txt")
    user_logger.log_automation_task("send_email", 2.5)
    
    # Get session statistics
    stats = user_logger.get_session_stats()
    print(f"Session stats: {json.dumps(stats, indent=2)}")
    
    # End session
    user_logger.end_session()
