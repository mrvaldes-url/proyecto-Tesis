import json
import logging
import boto3
import urllib.parse
import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Retrieve OpenSearch configuration from environment variables
OPENSEARCH_HOST = os.environ.get('OPENSEARCH_HOST')
OPENSEARCH_INDEX = os.environ.get('OPENSEARCH_INDEX', 'documents') # Default index name

# Initialize AWS clients
session = boto3.Session()
credentials = session.get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, session.region_name, 'es', session_token=credentials.token)

textract_client = session.client('textract')
comprehend_client = session.client('comprehend')

# Initialize OpenSearch client
opensearch_client = OpenSearch(
    hosts=[{'host': OPENSEARCH_HOST, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

def handler(event, context):
    """
    This Lambda function orchestrates the document processing pipeline:
    1. Triggered by an S3 upload.
    2. Extracts text using Amazon Textract.
    3. Analyzes text for entities using Amazon Comprehend.
    4. Indexes the text and metadata into Amazon OpenSearch.
    """
    if not OPENSEARCH_HOST:
        logger.error("FATAL: OPENSEARCH_HOST environment variable is not set.")
        return {'statusCode': 500, 'body': 'OpenSearch domain not configured.'}

    logger.info("## EVENT RECEIVED")
    # 1. Get bucket and key from the S3 event
    try:
        s3_record = event['Records'][0]['s3']
        s3_bucket = s3_record['bucket']['name']
        s3_key = urllib.parse.unquote_plus(s3_record['object']['key'])
        logger.info(f"Processing document: s3://{s3_bucket}/{s3_key}")
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing S3 event: {e}")
        return {'statusCode': 400, 'body': 'Invalid S3 event format'}

    # 2. Extract text with Textract
    try:
        response = textract_client.detect_document_text(Document={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}})
        detected_text = "".join([item["Text"] + "\n" for item in response.get("Blocks", []) if item["BlockType"] == "LINE"])
        if not detected_text:
            logger.warning("No text was detected in the document.")
            return {'statusCode': 200, 'body': 'No text detected.'}
        logger.info(f"Successfully extracted {len(detected_text)} characters of text.")
    except Exception as e:
        logger.error(f"Error calling Textract: {e}")
        return {'statusCode': 500, 'body': f'Error processing document with Textract: {e}'}

    # 3. Analyze text with Comprehend
    try:
        # Detect language
        lang_response = comprehend_client.detect_dominant_language(Text=detected_text[:5000])
        language_code = lang_response['Languages'][0]['LanguageCode']

        # Detect entities
        entities_response = comprehend_client.detect_entities(Text=detected_text[:5000], LanguageCode=language_code)
        entities = [{'Text': e['Text'], 'Type': e['Type']} for e in entities_response['Entities']]
        logger.info(f"Detected {len(entities)} entities with Comprehend.")
    except Exception as e:
        logger.error(f"Error calling Comprehend: {e}")
        # We can continue without Comprehend data if needed
        entities = []
        language_code = 'en' # Default language

    # 4. Index document in OpenSearch
    try:
        document = {
            's3_bucket': s3_bucket,
            's3_key': s3_key,
            'content': detected_text,
            'entities': entities,
            'language': language_code
        }
        # Use the S3 object key as the document ID to prevent duplicates
        doc_id = s3_key.replace('/', '_')

        response = opensearch_client.index(
            index=OPENSEARCH_INDEX,
            body=document,
            id=doc_id,
            refresh='wait_for' # Make the document searchable immediately
        )
        logger.info("## OPENSEARCH RESPONSE")
        logger.info(json.dumps(response, indent=2))
    except Exception as e:
        logger.error(f"Error indexing document in OpenSearch: {e}")
        return {'statusCode': 500, 'body': f'Error indexing document: {e}'}

    return {
        'statusCode': 200,
        'body': json.dumps('Document processed and indexed successfully!')
    }
