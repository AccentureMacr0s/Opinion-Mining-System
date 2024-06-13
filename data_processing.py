import boto3
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

s3_client = boto3.client('s3')

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = [w for w in word_tokens if not w.lower() in stop_words]
    return " ".join(filtered_text)

def lambda_handler(event, context):
    # Fetch data from S3
    bucket_name = event['bucket_name']
    key = event['key']
    obj = s3_client.get_object(Bucket=bucket_name, Key=key)
    comments = pd.read_json(obj['Body'])
    
    # Preprocess data
    comments['cleaned_text'] = comments['text'].apply(preprocess_text)
    
    # Store preprocessed data back to S3
    preprocessed_data = comments.to_json()
    store_data_to_s3(bucket_name, "preprocessed/comments.json", preprocessed_data)
    return {"statusCode": 200, "body": "Data preprocessed and stored in S3"}

# Deploy this script as an AWS Lambda function
