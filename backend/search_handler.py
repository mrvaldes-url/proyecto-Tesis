import json
import logging
import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Retrieve OpenSearch configuration from environment variables
OPENSEARCH_HOST = os.environ.get('OPENSEARCH_HOST')
OPENSEARCH_INDEX = os.environ.get('OPENSEARCH_INDEX', 'documents')

# Initialize AWS clients
session = boto3.Session()
credentials = session.get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, session.region_name, 'es', session_token=credentials.token)

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
    This Lambda function handles search queries from the frontend via API Gateway.
    It queries the OpenSearch index and returns matching documents.
    """
    if not OPENSEARCH_HOST:
        logger.error("FATAL: OPENSEARCH_HOST environment variable is not set.")
        return {'statusCode': 500, 'body': 'Search is not configured.'}

    # CORS headers for browser-based clients
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS'
    }

    try:
        # The search query is passed as a query string parameter, e.g., /search?q=my-term
        query_text = event['queryStringParameters']['q']
        if not query_text:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Query parameter "q" cannot be empty.'})
            }
        logger.info(f"Received search query: '{query_text}'")

        # Construct the OpenSearch query
        # This query searches the 'content' field for the given text.
        # It also highlights the matching text in the results.
        query = {
            "size": 20,
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["content", "entities.Text"]
                }
            },
            "highlight": {
                "fields": {
                    "content": {}
                }
            }
        }

        # Execute the search query
        response = opensearch_client.search(
            body=query,
            index=OPENSEARCH_INDEX
        )

        # Format the results for the frontend
        results = []
        for hit in response['hits']['hits']:
            result = {
                'score': hit['_score'],
                's3_key': hit['_source']['s3_key'],
                'language': hit['_source']['language'],
                'entities': hit['_source']['entities'],
                'highlight': hit.get('highlight', {}).get('content', [])
            }
            results.append(result)

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(results)
        }

    except KeyError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Missing required query parameter: "q"'})
        }
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'An error occurred while searching.'})
        }
