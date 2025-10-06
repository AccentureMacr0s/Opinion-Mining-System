"""
Database logging module for SpokyAI
Handles logging of user actions and system events to database
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import os

try:
    import boto3
    from boto3.dynamodb.conditions import Key
    DYNAMODB_AVAILABLE = True
except ImportError:
    DYNAMODB_AVAILABLE = False

try:
    from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# SQLAlchemy models
if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
    
    class UserActionLog(Base):
        """Model for user action logs"""
        __tablename__ = 'user_action_logs'
        
        id = Column(Integer, primary_key=True)
        timestamp = Column(DateTime, default=datetime.utcnow)
        user_id = Column(String(100))
        action_type = Column(String(100))
        action_details = Column(JSON)
        status = Column(String(50))
        metadata = Column(JSON)
    
    class SystemEventLog(Base):
        """Model for system event logs"""
        __tablename__ = 'system_event_logs'
        
        id = Column(Integer, primary_key=True)
        timestamp = Column(DateTime, default=datetime.utcnow)
        event_type = Column(String(100))
        event_details = Column(JSON)
        severity = Column(String(50))
        source = Column(String(100))
        metadata = Column(JSON)


class DatabaseLogger:
    """Main database logger class"""
    
    def __init__(self, db_type: str = "sqlite", connection_string: Optional[str] = None):
        """
        Initialize database logger
        
        Args:
            db_type: Type of database ('sqlite', 'dynamodb', 'postgresql', 'mysql')
            connection_string: Database connection string (optional)
        """
        self.db_type = db_type
        self.connection_string = connection_string or "sqlite:///spokyai_logs.db"
        
        if db_type == "dynamodb":
            if not DYNAMODB_AVAILABLE:
                raise ImportError("boto3 is required for DynamoDB logging")
            self._init_dynamodb()
        elif db_type in ["sqlite", "postgresql", "mysql"]:
            if not SQLALCHEMY_AVAILABLE:
                raise ImportError("sqlalchemy is required for SQL database logging")
            self._init_sqlalchemy()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _init_dynamodb(self):
        """Initialize DynamoDB connection"""
        self.dynamodb = boto3.resource('dynamodb')
        self.user_actions_table = self.dynamodb.Table('SpokyAI_UserActions')
        self.system_events_table = self.dynamodb.Table('SpokyAI_SystemEvents')
        logger.info("DynamoDB logger initialized")
    
    def _init_sqlalchemy(self):
        """Initialize SQLAlchemy connection"""
        self.engine = create_engine(self.connection_string)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logger.info(f"SQLAlchemy logger initialized with {self.db_type}")
    
    def log_user_action(
        self,
        user_id: str,
        action_type: str,
        action_details: Dict[str, Any],
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a user action to the database
        
        Args:
            user_id: User identifier
            action_type: Type of action (e.g., 'voice_command', 'mouse_click')
            action_details: Details of the action
            status: Status of the action ('success', 'failed', 'pending')
            metadata: Additional metadata
        """
        timestamp = datetime.utcnow()
        
        try:
            if self.db_type == "dynamodb":
                self.user_actions_table.put_item(
                    Item={
                        'user_id': user_id,
                        'timestamp': timestamp.isoformat(),
                        'action_type': action_type,
                        'action_details': json.dumps(action_details),
                        'status': status,
                        'metadata': json.dumps(metadata or {})
                    }
                )
            else:
                log_entry = UserActionLog(
                    timestamp=timestamp,
                    user_id=user_id,
                    action_type=action_type,
                    action_details=action_details,
                    status=status,
                    metadata=metadata or {}
                )
                self.session.add(log_entry)
                self.session.commit()
            
            logger.info(f"Logged user action: {action_type} for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log user action: {str(e)}")
            if self.db_type != "dynamodb":
                self.session.rollback()
    
    def log_system_event(
        self,
        event_type: str,
        event_details: Dict[str, Any],
        severity: str = "info",
        source: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a system event to the database
        
        Args:
            event_type: Type of event (e.g., 'startup', 'error', 'warning')
            event_details: Details of the event
            severity: Severity level ('info', 'warning', 'error', 'critical')
            source: Source of the event
            metadata: Additional metadata
        """
        timestamp = datetime.utcnow()
        
        try:
            if self.db_type == "dynamodb":
                self.system_events_table.put_item(
                    Item={
                        'timestamp': timestamp.isoformat(),
                        'event_type': event_type,
                        'event_details': json.dumps(event_details),
                        'severity': severity,
                        'source': source,
                        'metadata': json.dumps(metadata or {})
                    }
                )
            else:
                log_entry = SystemEventLog(
                    timestamp=timestamp,
                    event_type=event_type,
                    event_details=event_details,
                    severity=severity,
                    source=source,
                    metadata=metadata or {}
                )
                self.session.add(log_entry)
                self.session.commit()
            
            logger.info(f"Logged system event: {event_type} with severity {severity}")
        except Exception as e:
            logger.error(f"Failed to log system event: {str(e)}")
            if self.db_type != "dynamodb":
                self.session.rollback()
    
    def query_user_actions(
        self,
        user_id: Optional[str] = None,
        action_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ):
        """
        Query user actions from database
        
        Args:
            user_id: Filter by user ID
            action_type: Filter by action type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of results
        
        Returns:
            List of user action logs
        """
        try:
            if self.db_type == "dynamodb":
                # DynamoDB query implementation
                filter_expression = None
                if user_id:
                    response = self.user_actions_table.query(
                        KeyConditionExpression=Key('user_id').eq(user_id),
                        Limit=limit
                    )
                else:
                    response = self.user_actions_table.scan(Limit=limit)
                return response.get('Items', [])
            else:
                # SQLAlchemy query implementation
                query = self.session.query(UserActionLog)
                if user_id:
                    query = query.filter(UserActionLog.user_id == user_id)
                if action_type:
                    query = query.filter(UserActionLog.action_type == action_type)
                if start_time:
                    query = query.filter(UserActionLog.timestamp >= start_time)
                if end_time:
                    query = query.filter(UserActionLog.timestamp <= end_time)
                
                return query.limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to query user actions: {str(e)}")
            return []
    
    def close(self):
        """Close database connections"""
        if self.db_type != "dynamodb" and hasattr(self, 'session'):
            self.session.close()
            logger.info("Database connection closed")


# Convenience function for quick logging
def get_default_logger():
    """Get default database logger instance"""
    db_type = os.getenv('SPOKYAI_DB_TYPE', 'sqlite')
    connection_string = os.getenv('SPOKYAI_DB_CONNECTION')
    return DatabaseLogger(db_type=db_type, connection_string=connection_string)
