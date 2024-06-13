import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

def aggregate_sentiments():
    table = dynamodb.Table('SentimentResults')
    response = table.scan()
    items = response['Items']
    
    positive = sum(1 for item in items if item['sentiment'] == 'POSITIVE')
    negative = sum(1 for item in items if item['sentiment'] == 'NEGATIVE')
    neutral = sum(1 for item in items if item['sentiment'] == 'NEUTRAL')
    
    total = positive + negative + neutral
    rating = (positive - negative) / total * 100
    
    return {'positive': positive, 'negative': negative, 'neutral': neutral, 'rating': rating}

def lambda_handler(event, context):
    results = aggregate_sentiments()
    
    # Store rating in DynamoDB
    rating_table = dynamodb.Table('WebsiteRatings')
    rating_table.put_item(Item={'website_id': event['website_id'], 'rating': results['rating'], 'details': results})
    
    return {"statusCode": 200, "body": "Website rating calculated and stored in DynamoDB"}

# Deploy this script as an AWS Lambda function
