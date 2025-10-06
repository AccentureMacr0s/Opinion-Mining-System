import boto3
import requests
import logging
import json

# Configure logging for AWS Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def fetch_data(url):
    logger.info(f"Fetching data from URL: {url}")
    response = requests.get(url)
    logger.info(f"Data fetched successfully. Status code: {response.status_code}")
    return response.json()

def store_data_to_s3(bucket_name, key, data):
    logger.info(f"Storing data to S3: bucket={bucket_name}, key={key}")
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=data)
    logger.info("Data stored successfully to S3")

def lambda_handler(event, context):
    logger.info(f"Lambda function invoked with event: {json.dumps(event)}")
    try:
        data_url = "https://example.com/comments"
        data = fetch_data(data_url)
        store_data_to_s3("my-data-bucket", "raw/comments.json", data)
        logger.info("Lambda execution completed successfully")
        return {"statusCode": 200, "body": "Data fetched and stored in S3"}
    except Exception as e:
        logger.error(f"Error in lambda execution: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": f"Error: {str(e)}"}

# Deploy this script as an AWS Lambda function
