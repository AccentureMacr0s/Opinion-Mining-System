"""
Tests for Database Logger
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path
import tempfile
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Only test if sqlalchemy is available
try:
    from tools.database_logger import DatabaseLogger
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not installed")
class TestDatabaseLogger:
    """Test suite for DatabaseLogger"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield f"sqlite:///{path}"
        # Cleanup
        try:
            os.unlink(path)
        except:
            pass
    
    def test_initialization_sqlite(self, temp_db):
        """Test SQLite initialization"""
        logger = DatabaseLogger("sqlite", temp_db)
        assert logger.db_type == "sqlite"
        assert logger.connection_string == temp_db
    
    def test_log_user_action(self, temp_db):
        """Test logging user action"""
        logger = DatabaseLogger("sqlite", temp_db)
        
        logger.log_user_action(
            user_id="test_user",
            action_type="test_action",
            action_details={"key": "value"},
            status="success"
        )
        
        # Query to verify
        actions = logger.query_user_actions(user_id="test_user")
        assert len(actions) == 1
        assert actions[0].action_type == "test_action"
    
    def test_log_system_event(self, temp_db):
        """Test logging system event"""
        logger = DatabaseLogger("sqlite", temp_db)
        
        logger.log_system_event(
            event_type="test_event",
            event_details={"detail": "test"},
            severity="info"
        )
        
        # No error means success
        assert True
    
    def test_query_user_actions_with_filters(self, temp_db):
        """Test querying with filters"""
        logger = DatabaseLogger("sqlite", temp_db)
        
        # Add multiple actions
        logger.log_user_action("user1", "action1", {})
        logger.log_user_action("user1", "action2", {})
        logger.log_user_action("user2", "action1", {})
        
        # Query for user1
        user1_actions = logger.query_user_actions(user_id="user1")
        assert len(user1_actions) == 2
        
        # Query for action1
        action1_logs = logger.query_user_actions(action_type="action1")
        assert len(action1_logs) == 2
    
    def test_query_with_time_range(self, temp_db):
        """Test querying with time range"""
        logger = DatabaseLogger("sqlite", temp_db)
        
        logger.log_user_action("user1", "action1", {})
        
        # Query with time range
        end_time = datetime.utcnow()
        actions = logger.query_user_actions(
            user_id="user1",
            end_time=end_time
        )
        assert len(actions) >= 1
    
    def test_close_connection(self, temp_db):
        """Test closing database connection"""
        logger = DatabaseLogger("sqlite", temp_db)
        logger.close()
        # No error means success
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
