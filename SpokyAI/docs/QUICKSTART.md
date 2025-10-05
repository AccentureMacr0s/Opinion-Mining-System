# SpokyAI Quick Start Guide

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/AccentureMacr0s/Opinion-Mining-System.git
cd Opinion-Mining-System/SpokyAI
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Download Vosk model for voice recognition
```bash
# Download a small English model
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 models/vosk-model
```

## Basic Usage

### Using the User Action Logger

```python
from SpokyAI.core import UserActionLogger

# Create a logger
logger = UserActionLogger("user_123")

# Log different types of actions
logger.log_mouse_click(100, 200, "left")
logger.log_keyboard_input("Hello World", "text_editor")
logger.log_voice_command("open browser", "open browser", 0.95)

# Get session statistics
stats = logger.get_session_stats()
print(stats)

# End session
logger.end_session()
```

### Using Voice Recognition

```python
from SpokyAI.ai import VoiceRecognition, VoiceCommandHandler

# Initialize voice recognition
vr = VoiceRecognition(model_path="models/vosk-model")
handler = VoiceCommandHandler(vr)

# Register commands
def hello_command():
    print("Hello! SpokyAI is listening.")

handler.register_command("hello spoky", hello_command)

# Start listening
handler.start_listening()

# ... your code here ...

# Stop when done
handler.stop_listening()
vr.cleanup()
```

### Using Database Logger

```python
from SpokyAI.tools import DatabaseLogger

# Initialize with SQLite
db_logger = DatabaseLogger("sqlite", "sqlite:///my_logs.db")

# Log a user action
db_logger.log_user_action(
    user_id="user_123",
    action_type="click",
    action_details={"x": 100, "y": 200},
    status="success"
)

# Query actions
actions = db_logger.query_user_actions(user_id="user_123", limit=10)
for action in actions:
    print(f"{action.timestamp}: {action.action_type}")

# Close connection
db_logger.close()
```

### Running the Main Agent

```bash
# Basic usage
python core/agent.py

# With specific user ID
python core/agent.py --user "my_user_id"
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Run specific test file
pytest tests/test_user_logger.py -v
```

## Configuration

Edit `config/config.yaml` to customize:
- System resource limits
- Voice recognition settings
- Database configuration
- AWS integration
- Security settings

## AWS Lambda Deployment

### Deploy a Lambda function:

```bash
cd lambda/
zip -r function.zip data_storage.py

aws lambda create-function \
  --function-name spokyai-data-storage \
  --runtime python3.10 \
  --handler data_storage.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-role
```

## Troubleshooting

### Voice recognition not working
- Check if microphone is connected: `arecord -l`
- Verify Vosk model is downloaded to correct path
- Check sample rate matches your microphone

### Import errors
- Ensure you're in the correct directory
- Install all dependencies: `pip install -r requirements.txt`
- Some features require optional dependencies

### Database errors
- Check database file permissions
- Verify connection string format
- Ensure SQLAlchemy is installed for SQL databases

## Next Steps

- Read the full documentation in `docs/README.md`
- Check example scripts in `examples/` (coming soon)
- Join the community on GitHub Discussions

## Support

- GitHub Issues: https://github.com/AccentureMacr0s/Opinion-Mining-System/issues
- Documentation: `docs/README.md`
