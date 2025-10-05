"""SpokyAI AI Module"""

try:
    from .voice_recognition import VoiceRecognition, VoiceCommandHandler
    __all__ = ['VoiceRecognition', 'VoiceCommandHandler']
except ImportError:
    __all__ = []
