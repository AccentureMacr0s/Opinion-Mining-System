"""
Speech Recognition Module for SpokyAI using Vosk
Handles voice input and command recognition
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import queue
import threading

try:
    import vosk
    import pyaudio
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    print("Warning: vosk or pyaudio not installed. Voice recognition will not be available.")

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class VoiceRecognition:
    """Voice recognition engine using Vosk"""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        sample_rate: int = 16000,
        buffer_size: int = 4000
    ):
        """
        Initialize voice recognition
        
        Args:
            model_path: Path to Vosk model directory
            sample_rate: Audio sample rate (Hz)
            buffer_size: Audio buffer size
        """
        if not VOSK_AVAILABLE:
            raise ImportError("vosk and pyaudio are required for voice recognition")
        
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.is_listening = False
        self.audio_queue = queue.Queue()
        
        # Initialize Vosk model
        if model_path is None:
            # Try to find model in default locations
            model_path = self._find_model()
        
        if model_path and os.path.exists(model_path):
            logger.info(f"Loading Vosk model from: {model_path}")
            self.model = vosk.Model(model_path)
        else:
            logger.warning("Vosk model not found. Please download a model from https://alphacephei.com/vosk/models")
            self.model = None
        
        # Initialize recognizer
        if self.model:
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)
        else:
            self.recognizer = None
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        logger.info("Voice recognition initialized")
    
    def _find_model(self) -> Optional[str]:
        """Try to find Vosk model in common locations"""
        possible_paths = [
            Path.home() / ".cache" / "vosk" / "model",
            Path(__file__).parent.parent / "models" / "vosk-model",
            Path("/usr/share/vosk/model"),
            Path("vosk-model"),
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "am").exists():
                return str(path)
        
        return None
    
    def start_listening(self, callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Start listening for voice input
        
        Args:
            callback: Function to call with recognition results
        """
        if not self.recognizer:
            logger.error("Recognizer not initialized. Cannot start listening.")
            return
        
        if self.is_listening:
            logger.warning("Already listening")
            return
        
        self.is_listening = True
        
        # Start audio stream
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.buffer_size,
            stream_callback=self._audio_callback
        )
        
        self.stream.start_stream()
        
        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._process_audio,
            args=(callback,),
            daemon=True
        )
        self.processing_thread.start()
        
        logger.info("Started listening for voice input")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def _process_audio(self, callback: Optional[Callable[[Dict[str, Any]], None]]):
        """Process audio data from queue"""
        while self.is_listening:
            try:
                data = self.audio_queue.get(timeout=1)
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    logger.info(f"Recognition result: {result}")
                    
                    if callback and result.get('text'):
                        callback(result)
                else:
                    partial = json.loads(self.recognizer.PartialResult())
                    if partial.get('partial'):
                        logger.debug(f"Partial result: {partial['partial']}")
            
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing audio: {str(e)}")
    
    def stop_listening(self):
        """Stop listening for voice input"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        logger.info("Stopped listening")
    
    def recognize_from_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Recognize speech from audio data
        
        Args:
            audio_data: Raw audio data (16-bit PCM)
        
        Returns:
            Recognition result dictionary
        """
        if not self.recognizer:
            return {"error": "Recognizer not initialized"}
        
        if self.recognizer.AcceptWaveform(audio_data):
            result = json.loads(self.recognizer.Result())
        else:
            result = json.loads(self.recognizer.PartialResult())
        
        return result
    
    def recognize_from_file(self, file_path: str) -> str:
        """
        Recognize speech from audio file
        
        Args:
            file_path: Path to audio file (WAV format, 16 kHz)
        
        Returns:
            Recognized text
        """
        if not self.recognizer:
            return ""
        
        import wave
        
        with wave.open(file_path, "rb") as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != self.sample_rate:
                logger.error("Audio file must be WAV format mono PCM.")
                return ""
            
            results = []
            
            while True:
                data = wf.readframes(self.buffer_size)
                if len(data) == 0:
                    break
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if result.get('text'):
                        results.append(result['text'])
            
            # Get final result
            final_result = json.loads(self.recognizer.FinalResult())
            if final_result.get('text'):
                results.append(final_result['text'])
            
            return " ".join(results)
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_listening()
        if self.audio:
            self.audio.terminate()
        logger.info("Voice recognition cleanup completed")


class VoiceCommandHandler:
    """Handler for processing voice commands"""
    
    def __init__(self, voice_recognition: VoiceRecognition):
        """
        Initialize command handler
        
        Args:
            voice_recognition: VoiceRecognition instance
        """
        self.voice_recognition = voice_recognition
        self.commands: Dict[str, Callable] = {}
        logger.info("Voice command handler initialized")
    
    def register_command(self, command: str, handler: Callable):
        """
        Register a voice command handler
        
        Args:
            command: Command phrase
            handler: Function to call when command is recognized
        """
        self.commands[command.lower()] = handler
        logger.info(f"Registered command: {command}")
    
    def process_result(self, result: Dict[str, Any]):
        """
        Process recognition result and execute commands
        
        Args:
            result: Recognition result from Vosk
        """
        text = result.get('text', '').lower().strip()
        
        if not text:
            return
        
        logger.info(f"Processing command: {text}")
        
        # Check for exact matches
        if text in self.commands:
            logger.info(f"Executing command: {text}")
            self.commands[text]()
            return
        
        # Check for partial matches
        for command, handler in self.commands.items():
            if command in text:
                logger.info(f"Executing command (partial match): {command}")
                handler()
                return
        
        logger.info(f"No command found for: {text}")
    
    def start_listening(self):
        """Start listening for commands"""
        self.voice_recognition.start_listening(callback=self.process_result)
    
    def stop_listening(self):
        """Stop listening for commands"""
        self.voice_recognition.stop_listening()


# Example usage
if __name__ == "__main__":
    # Initialize voice recognition
    vr = VoiceRecognition()
    
    # Create command handler
    handler = VoiceCommandHandler(vr)
    
    # Register some example commands
    def hello_command():
        print("Hello! SpokyAI is listening.")
    
    def goodbye_command():
        print("Goodbye!")
        handler.stop_listening()
    
    handler.register_command("hello spoky", hello_command)
    handler.register_command("goodbye spoky", goodbye_command)
    
    # Start listening
    print("Starting voice recognition. Say 'hello spoky' or 'goodbye spoky'")
    handler.start_listening()
    
    # Keep running
    try:
        import time
        while vr.is_listening:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        handler.stop_listening()
        vr.cleanup()
