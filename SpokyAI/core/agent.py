"""
Main SpokyAI Agent Entry Point
Example implementation showing how to use SpokyAI components
"""

import sys
import signal
import logging
from pathlib import Path

# Add SpokyAI to path
sys.path.insert(0, str(Path(__file__).parent))

from core.user_action_logger import UserActionLogger
from tools.database_logger import DatabaseLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpokyAgent:
    """Main SpokyAI Agent"""
    
    def __init__(self, user_id: str = "default_user"):
        """
        Initialize SpokyAI Agent
        
        Args:
            user_id: User identifier
        """
        self.user_id = user_id
        self.running = False
        
        # Initialize components
        logger.info(f"Initializing SpokyAI Agent for user: {user_id}")
        
        # User action logger
        self.action_logger = UserActionLogger(user_id)
        
        # Database logger (optional, depends on configuration)
        try:
            self.db_logger = DatabaseLogger("sqlite", "sqlite:///spokyai_logs.db")
            logger.info("Database logger initialized")
        except Exception as e:
            logger.warning(f"Database logger not available: {e}")
            self.db_logger = None
        
        # Voice recognition (optional, depends on Vosk being available)
        try:
            from ai.voice_recognition import VoiceRecognition, VoiceCommandHandler
            self.voice_recognition = VoiceRecognition()
            self.command_handler = VoiceCommandHandler(self.voice_recognition)
            self._register_voice_commands()
            logger.info("Voice recognition initialized")
        except Exception as e:
            logger.warning(f"Voice recognition not available: {e}")
            self.voice_recognition = None
            self.command_handler = None
        
        logger.info("SpokyAI Agent initialized successfully")
    
    def _register_voice_commands(self):
        """Register voice commands"""
        if not self.command_handler:
            return
        
        # Register example commands
        self.command_handler.register_command("hello spoky", self.cmd_hello)
        self.command_handler.register_command("goodbye spoky", self.cmd_goodbye)
        self.command_handler.register_command("status", self.cmd_status)
        self.command_handler.register_command("help", self.cmd_help)
        
        logger.info("Voice commands registered")
    
    def cmd_hello(self):
        """Hello command"""
        logger.info("Hello command received")
        print("Hello! SpokyAI is listening and ready to help.")
        self.action_logger.log_voice_command("hello", "hello spoky", 1.0)
    
    def cmd_goodbye(self):
        """Goodbye command"""
        logger.info("Goodbye command received")
        print("Goodbye! SpokyAI is shutting down.")
        self.action_logger.log_voice_command("goodbye", "goodbye spoky", 1.0)
        self.stop()
    
    def cmd_status(self):
        """Status command"""
        logger.info("Status command received")
        stats = self.action_logger.get_session_stats()
        print(f"SpokyAI Status:")
        print(f"  User: {stats['user_id']}")
        print(f"  Session duration: {stats['session_duration_seconds']:.2f} seconds")
        print(f"  Total actions: {stats['total_actions']}")
        self.action_logger.log_voice_command("status", "status", 1.0)
    
    def cmd_help(self):
        """Help command"""
        logger.info("Help command received")
        print("SpokyAI Voice Commands:")
        print("  - 'hello spoky' - Greet SpokyAI")
        print("  - 'goodbye spoky' - Exit SpokyAI")
        print("  - 'status' - Show current status")
        print("  - 'help' - Show this help message")
        self.action_logger.log_voice_command("help", "help", 1.0)
    
    def start(self):
        """Start the agent"""
        self.running = True
        logger.info("Starting SpokyAI Agent")
        
        # Start voice recognition if available
        if self.command_handler:
            print("Starting voice recognition...")
            print("Say 'hello spoky', 'status', 'help', or 'goodbye spoky'")
            self.command_handler.start_listening()
        else:
            print("Voice recognition not available. Running in limited mode.")
            print("Press Ctrl+C to exit.")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Main loop
        try:
            while self.running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        
        self.stop()
    
    def stop(self):
        """Stop the agent"""
        if not self.running:
            return
        
        logger.info("Stopping SpokyAI Agent")
        self.running = False
        
        # Stop voice recognition
        if self.command_handler:
            self.command_handler.stop_listening()
        
        if self.voice_recognition:
            self.voice_recognition.cleanup()
        
        # End logging session
        self.action_logger.end_session()
        
        # Close database connection
        if self.db_logger:
            self.db_logger.close()
        
        logger.info("SpokyAI Agent stopped")
        print("SpokyAI Agent stopped successfully.")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals"""
        logger.info(f"Signal {signum} received")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SpokyAI - Intelligent AI Agent")
    parser.add_argument("--user", type=str, default="default_user", help="User ID")
    parser.add_argument("--version", action="version", version="SpokyAI 0.1.0")
    
    args = parser.parse_args()
    
    # Create and start agent
    agent = SpokyAgent(user_id=args.user)
    agent.start()


if __name__ == "__main__":
    main()
