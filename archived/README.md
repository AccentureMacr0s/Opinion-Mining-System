# Archived Components

This directory contains archived components that are not part of the core SpokyAI agent functionality.

## Contents

### lambda/
AWS Lambda functions for the opinion mining system:
- `data_storage.py` - S3 data storage function
- `data_processing.py` - Text preprocessing function
- `sentiment_analysis.py` - Sentiment analysis function
- `rating_evaluation.py` - Rating calculation function

These were part of the original Opinion Mining System architecture but are not needed for the SpokyAI agent, which focuses on learning user behavior through logs and responding to speech requests.

### opinion-mining-system/
Original opinion mining system Python files that were in the root directory. These are preserved for reference but are not part of the SpokyAI agent implementation.

## Why Archived?

The SpokyAI agent is designed to:
- Learn from user behavior through logs
- Monitor keyboard and mouse actions
- Respond to speech requests
- Develop a mindset based on gathered data
- Interact with the Windows interface

The opinion mining and AWS Lambda components serve a different purpose and have been archived to keep the project focused on the core agent functionality.
