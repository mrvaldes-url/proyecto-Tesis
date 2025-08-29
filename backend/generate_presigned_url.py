import json
import logging
import boto3
import os
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Boto3 client
s3_client = boto3.client('s3')

# Retrieve the S3 bucket name from environment variables
UPLOAD_BUCKET = os.environ.get('UPLOAD_BUCKET')

def handler(event, context):
    """
    This Lambda function generates a pre-signed URL for uploading a file to S3.
    It is triggered by an API Gateway request.

    The client must provide a 'fileName' in the request body.
    """
    if not UPLOAD_BUCKET:
        logger.error("FATAL: UPLOAD_BUCKET environment variable is not set.")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Server-side bucket not configured.'})
        }

    try:
        # The body from API Gateway is a string, so we need to parse it.
        body = json.loads(event.get('body', '{}'))
        file_name = body.get('fileName')

        if not file_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'fileName must be provided in the request body.'})
            }

        # Generate the pre-signed URL for a PUT request
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': UPLOAD_BUCKET, 'Key': file_name},
            ExpiresIn=3600  # URL expires in 1 hour
        )

        return {
            'statusCode': 200,
            # CORS headers are important for browser-based calls
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'uploadUrl': presigned_url, 'fileName': file_name})
        }

    except ClientError as e:
        logger.error(f"Error generating pre-signed URL: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Could not generate upload URL.'})
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body.'})
        }
