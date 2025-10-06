import boto3
from transformers import pipeline
import pandas as pd
import logging
import json

# Configure logging for AWS Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

sentiment_analysis = pipeline('sentiment-analysis')

def analyze_sentiment(text):
    result = sentiment_analysis(text)
    return result[0]['label']

def lambda_handler(event, context):
    logger.info(f"Lambda function invoked with event: {json.dumps(event)}")
    try:
        # Fetch preprocessed data from S3
        bucket_name = event['bucket_name']
        key = event['key']
        logger.info(f"Fetching preprocessed data from S3: bucket={bucket_name}, key={key}")
        obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        comments = pd.read_json(obj['Body'])
        logger.info(f"Data fetched successfully. Analyzing sentiment for {len(comments)} comments")
        
        # Perform sentiment analysis
        comments['sentiment'] = comments['cleaned_text'].apply(analyze_sentiment)
        logger.info("Sentiment analysis completed")
        
        # Store results in DynamoDB
        table = dynamodb.Table('SentimentResults')
        for _, row in comments.iterrows():
            table.put_item(Item={'comment_id': row['id'], 'text': row['text'], 'sentiment': row['sentiment']})
        logger.info(f"Stored {len(comments)} sentiment results in DynamoDB")
        
        logger.info("Lambda execution completed successfully")
        return {"statusCode": 200, "body": "Sentiment analysis completed and results stored in DynamoDB"}
    except Exception as e:
        logger.error(f"Error in lambda execution: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": f"Error: {str(e)}"}

# Deploy this script as an AWS Lambda function
