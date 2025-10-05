"""
Tests for User Action Logger
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.user_action_logger import UserActionLogger, get_logger


class TestUserActionLogger:
    """Test suite for UserActionLogger"""
    
    def test_initialization(self):
        """Test logger initialization"""
        logger = UserActionLogger("test_user")
        assert logger.user_id == "test_user"
        assert logger.action_count >= 1  # session_start is logged
        assert logger.session_start is not None
    
    def test_log_action(self):
        """Test basic action logging"""
        logger = UserActionLogger("test_user")
        initial_count = logger.action_count
        
        logger.log_action("test_action", {"key": "value"})
        
        assert logger.action_count == initial_count + 1
    
    def test_log_mouse_click(self):
        """Test mouse click logging"""
        logger = UserActionLogger("test_user")
        initial_count = logger.action_count
        
        logger.log_mouse_click(100, 200, "left")
        
        assert logger.action_count == initial_count + 1
    
    def test_log_keyboard_input(self):
        """Test keyboard input logging"""
        logger = UserActionLogger("test_user")
        initial_count = logger.action_count
        
        logger.log_keyboard_input("test input", "context")
        
        assert logger.action_count == initial_count + 1
    
    def test_log_voice_command(self):
        """Test voice command logging"""
        logger = UserActionLogger("test_user")
        initial_count = logger.action_count
        
        logger.log_voice_command("open browser", "open browser", 0.95)
        
        assert logger.action_count == initial_count + 1
    
    def test_log_window_switch(self):
        """Test window switch logging"""
        logger = UserActionLogger("test_user")
        initial_count = logger.action_count
        
        logger.log_window_switch("Terminal", "Chrome")
        
        assert logger.action_count == initial_count + 1
    
    def test_log_file_operation(self):
        """Test file operation logging"""
        logger = UserActionLogger("test_user")
        initial_count = logger.action_count
        
        logger.log_file_operation("open", "/path/to/file.txt")
        
        assert logger.action_count == initial_count + 1
    
    def test_log_automation_task(self):
        """Test automation task logging"""
        logger = UserActionLogger("test_user")
        initial_count = logger.action_count
        
        logger.log_automation_task("test_task", 2.5)
        
        assert logger.action_count == initial_count + 1
    
    def test_log_error(self):
        """Test error logging"""
        logger = UserActionLogger("test_user")
        initial_count = logger.action_count
        
        logger.log_error("ValueError", "Test error", {"context": "test"})
        
        assert logger.action_count == initial_count + 1
    
    def test_get_session_stats(self):
        """Test session statistics"""
        logger = UserActionLogger("test_user")
        
        stats = logger.get_session_stats()
        
        assert "user_id" in stats
        assert stats["user_id"] == "test_user"
        assert "session_start" in stats
        assert "session_duration_seconds" in stats
        assert "total_actions" in stats
        assert stats["total_actions"] >= 1
    
    def test_end_session(self):
        """Test session ending"""
        logger = UserActionLogger("test_user")
        initial_count = logger.action_count
        
        logger.end_session()
        
        assert logger.action_count == initial_count + 1
    
    def test_get_logger_singleton(self):
        """Test get_logger returns same instance"""
        logger1 = get_logger("test_user")
        logger2 = get_logger("test_user")
        
        # Both should reference the same object
        assert logger1 is logger2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
