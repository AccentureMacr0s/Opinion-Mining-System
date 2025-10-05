"""
SpokyAI Package
Intelligent AI agent for user action automation and voice control
"""

__version__ = "0.1.0"
__author__ = "Opinion-Mining-System Team"

# Import main components
try:
    from .core import UserActionLogger, get_logger
    from .ai import VoiceRecognition, VoiceCommandHandler
    from .tools import DatabaseLogger
    
    __all__ = [
        'UserActionLogger',
        'get_logger',
        'VoiceRecognition',
        'VoiceCommandHandler',
        'DatabaseLogger'
    ]
except ImportError as e:
    # Some optional dependencies might not be installed
    __all__ = []
