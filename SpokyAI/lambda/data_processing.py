import boto3
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging
import json

# Configure logging for AWS Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

nltk.download('punkt')
nltk.download('stopwords')

s3_client = boto3.client('s3')

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = [w for w in word_tokens if not w.lower() in stop_words]
    return " ".join(filtered_text)

def lambda_handler(event, context):
    logger.info(f"Lambda function invoked with event: {json.dumps(event)}")
    try:
        # Fetch data from S3
        bucket_name = event['bucket_name']
        key = event['key']
        logger.info(f"Fetching data from S3: bucket={bucket_name}, key={key}")
        obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        comments = pd.read_json(obj['Body'])
        logger.info(f"Data fetched successfully. Processing {len(comments)} comments")
        
        # Preprocess data
        comments['cleaned_text'] = comments['text'].apply(preprocess_text)
        logger.info("Text preprocessing completed")
        
        # Store preprocessed data back to S3
        preprocessed_data = comments.to_json()
        from data_storage import store_data_to_s3
        store_data_to_s3(bucket_name, "preprocessed/comments.json", preprocessed_data)
        logger.info("Lambda execution completed successfully")
        return {"statusCode": 200, "body": "Data preprocessed and stored in S3"}
    except Exception as e:
        logger.error(f"Error in lambda execution: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": f"Error: {str(e)}"}

# Deploy this script as an AWS Lambda function
