import boto3
import requests

s3_client = boto3.client('s3')

def fetch_data(url):
    response = requests.get(url)
    return response.json()

def store_data_to_s3(bucket_name, key, data):
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=data)

def lambda_handler(event, context):
    data_url = "https://example.com/comments"
    data = fetch_data(data_url)
    store_data_to_s3("my-data-bucket", "raw/comments.json", data)
    return {"statusCode": 200, "body": "Data fetched and stored in S3"}

# Deploy this script as an AWS Lambda function
