# SpokyAI Documentation

## Table of Contents
1. [Getting Started](#getting-started)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [API Reference](#api-reference)
5. [Configuration](#configuration)
6. [AWS Integration](#aws-integration)

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Minimum 4GB RAM
- Microphone for voice recognition

### Quick Start

1. Install dependencies:
```bash
cd SpokyAI
pip install -r requirements.txt
```

2. Download Vosk model:
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/
```

3. Run example:
```python
from SpokyAI.core import UserActionLogger
from SpokyAI.ai import VoiceRecognition

# Create action logger
logger = UserActionLogger("user_123")

# Log an action
logger.log_action("test_action", {"detail": "example"})
```

## Architecture

SpokyAI follows a modular architecture:

```
┌─────────────────────────────────────┐
│         User Interface              │
│  (Voice/Keyboard/Mouse Input)       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│      Voice Recognition (AI)         │
│        Command Processing           │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│      Core Agent Logic               │
│   (Action Execution & Logging)      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    Tools & Utilities                │
│  (Database, Automation, etc.)       │
└─────────────────────────────────────┘
```

## Core Components

### User Action Logger
Tracks and logs all user interactions:

```python
from SpokyAI.core import UserActionLogger

logger = UserActionLogger("user_id")
logger.log_mouse_click(100, 200, "left")
logger.log_keyboard_input("Hello", "text_editor")
logger.log_voice_command("open browser", "open browser", 0.95)
```

### Voice Recognition
Speech-to-text using Vosk:

```python
from SpokyAI.ai import VoiceRecognition, VoiceCommandHandler

# Initialize
vr = VoiceRecognition(model_path="models/vosk-model")
handler = VoiceCommandHandler(vr)

# Register commands
handler.register_command("hello", lambda: print("Hello!"))

# Start listening
handler.start_listening()
```

### Database Logger
Persistent logging to database:

```python
from SpokyAI.tools import DatabaseLogger

# SQLite
db_logger = DatabaseLogger("sqlite", "sqlite:///logs.db")

# Log user action
db_logger.log_user_action(
    user_id="user_123",
    action_type="click",
    action_details={"x": 100, "y": 200}
)

# Query logs
actions = db_logger.query_user_actions(user_id="user_123", limit=10)
```

## Configuration

Configuration is managed through `config/config.yaml`:

### System Configuration
```yaml
system:
  max_cpu_percent: 80
  max_ram_mb: 2048
  log_level: INFO
```

### Voice Recognition
```yaml
voice:
  enabled: true
  model_path: models/vosk-model
  sample_rate: 16000
  activation_phrase: "hey spoky"
```

### Database
```yaml
database:
  type: sqlite
  connection_string: sqlite:///spokyai_logs.db
```

## AWS Integration

### Lambda Functions

SpokyAI includes AWS Lambda functions for cloud processing:

#### Data Storage
```python
# lambda/data_storage.py
# Fetches and stores data in S3
```

#### Data Processing
```python
# lambda/data_processing.py
# Preprocesses text data with NLTK
```

#### Sentiment Analysis
```python
# lambda/sentiment_analysis.py
# Analyzes sentiment using transformers
```

#### Rating Evaluation
```python
# lambda/rating_evaluation.py
# Calculates website ratings
```

### Deployment

1. Package Lambda function:
```bash
cd SpokyAI/lambda
zip -r function.zip data_storage.py
```

2. Deploy with AWS CLI:
```bash
aws lambda create-function \
  --function-name spokyai-data-storage \
  --runtime python3.10 \
  --handler data_storage.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role
```

## Testing

Run tests with pytest:

```bash
# All tests
pytest SpokyAI/tests/

# With coverage
pytest --cov=SpokyAI SpokyAI/tests/

# Specific test
pytest SpokyAI/tests/test_user_logger.py
```

## Troubleshooting

### Voice Recognition Issues
- Ensure microphone is connected and working
- Check model path in configuration
- Verify sample rate matches audio input

### Database Connection Issues
- Check connection string format
- Verify database file permissions
- Ensure SQLAlchemy is installed for SQL databases

### Lambda Function Issues
- Check CloudWatch logs for errors
- Verify IAM role permissions
- Ensure all dependencies are packaged

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
