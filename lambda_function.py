import json
import boto3
import os
import uuid
from datetime import datetime

# Get the DynamoDB table name from environment variables
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'think-from-zero-form-submissions')

# Create a DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)

def lambda_handler(event, context):
    """
    This function handles the form submission from the static website.
    It expects a POST request with a JSON body containing the form data.
    """
    try:
        # The form data is in the 'body' of the event from API Gateway
        form_data = json.loads(event['body'])

        # Extract form fields
        name = form_data.get('name')
        email = form_data.get('email')
        phone = form_data.get('phone')
        problem = form_data.get('problem')

        # Basic validation
        if not name or not email or not problem:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*', # Allow requests from any origin
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'message': 'Missing required fields: name, email, and problem are required.'})
            }

        # Create a unique ID for the submission
        submission_id = str(uuid.uuid4())

        # Get the current timestamp
        timestamp = datetime.utcnow().isoformat()

        # Create the item to save to DynamoDB
        item = {
            'id': submission_id,
            'createdAt': timestamp,
            'name': name,
            'email': email,
            'phone': phone,
            'problem': problem
        }

        # Save the item to the DynamoDB table
        table.put_item(Item=item)

        # Return a success response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'message': 'Form submitted successfully!'})
        }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'message': 'Invalid JSON in request body.'})
        }
    except Exception as e:
        # Log the error for debugging
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'message': 'An error occurred. Please try again later.'})
        }
