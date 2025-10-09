import boto3
from transformers import pipeline

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

sentiment_analysis = pipeline('sentiment-analysis')

def analyze_sentiment(text):
    result = sentiment_analysis(text)
    return result[0]['label']

def lambda_handler(event, context):
    # Fetch preprocessed data from S3
    bucket_name = event['bucket_name']
    key = event['key']
    obj = s3_client.get_object(Bucket=bucket_name, Key=key)
    comments = pd.read_json(obj['Body'])
    
    # Perform sentiment analysis
    comments['sentiment'] = comments['cleaned_text'].apply(analyze_sentiment)
    
    # Store results in DynamoDB
    table = dynamodb.Table('SentimentResults')
    for _, row in comments.iterrows():
        table.put_item(Item={'comment_id': row['id'], 'text': row['text'], 'sentiment': row['sentiment']})
    
    return {"statusCode": 200, "body": "Sentiment analysis completed and results stored in DynamoDB"}

# Deploy this script as an AWS Lambda function
