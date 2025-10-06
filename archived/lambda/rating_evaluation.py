import boto3
from boto3.dynamodb.conditions import Key
import logging
import json

# Configure logging for AWS Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')

def aggregate_sentiments():
    logger.info("Aggregating sentiments from DynamoDB")
    table = dynamodb.Table('SentimentResults')
    response = table.scan()
    items = response['Items']
    
    positive = sum(1 for item in items if item['sentiment'] == 'POSITIVE')
    negative = sum(1 for item in items if item['sentiment'] == 'NEGATIVE')
    neutral = sum(1 for item in items if item['sentiment'] == 'NEUTRAL')
    
    total = positive + negative + neutral
    rating = (positive - negative) / total * 100 if total > 0 else 0
    
    logger.info(f"Aggregation results: positive={positive}, negative={negative}, neutral={neutral}, rating={rating}")
    return {'positive': positive, 'negative': negative, 'neutral': neutral, 'rating': rating}

def lambda_handler(event, context):
    logger.info(f"Lambda function invoked with event: {json.dumps(event)}")
    try:
        results = aggregate_sentiments()
        
        # Store rating in DynamoDB
        rating_table = dynamodb.Table('WebsiteRatings')
        website_id = event['website_id']
        rating_table.put_item(Item={'website_id': website_id, 'rating': results['rating'], 'details': results})
        logger.info(f"Rating stored for website_id: {website_id}")
        
        logger.info("Lambda execution completed successfully")
        return {"statusCode": 200, "body": "Website rating calculated and stored in DynamoDB"}
    except Exception as e:
        logger.error(f"Error in lambda execution: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": f"Error: {str(e)}"}

# Deploy this script as an AWS Lambda function
