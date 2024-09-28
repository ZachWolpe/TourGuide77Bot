"""
-------------------------------------------------------------------------------------
AWS Lambda function to handle Telegram API calls.

This script contains the main logic for the Telegram bot.

> Initialises the bot and sets up the commands.
> Handles the start, help, custom, travel_tips, and google_map commands.
> Query the Gemini API.
> Respond to messages.

Functions to handle async Telegram API calls.

: zach.wolpe@medibio.com.au
: 27:09:2024
-------------------------------------------------------------------------------------
"""
from telegram_api_helpers import send_message

import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import logging
import boto3
import json
import os

from telegram_api_helpers import (event_instance, handle_message)


# load env --------------------------------------------------------------------------------------------->>
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv()
BOT_API_TOKEN: str = os.getenv("BOT_API_TOKEN")
BOT_USERNAME: str = os.getenv("BOT_USERNAME")
DYNAMODB_TABLE: str = os.getenv("RATE_LIMIT_TABLE")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# load env --------------------------------------------------------------------------------------------->>

# Initialise DynamoDB client --------------------------------------------------------------------------->>
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)
RATE_LIMIT = 10  # requests
TIME_WINDOW = 60  # seconds
# Initialise DynamoDB client --------------------------------------------------------------------------->>


def check_rate_limit(user_id):
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(seconds=TIME_WINDOW)

    # Update the request count
    response = table.update_item(
        Key={'user_id': str(user_id)},
        UpdateExpression='SET request_count = if_not_exists(request_count, :zero) + :inc, last_request = :now',
        ExpressionAttributeValues={
            ':inc': 1,
            ':now': now.isoformat(),
            ':zero': 0,
            ':window_start': start_time.isoformat(),
            ':limit': RATE_LIMIT
        },
        ConditionExpression='attribute_not_exists(last_request) OR last_request < :window_start OR request_count < :limit',
        ReturnValues='UPDATED_NEW'
    )

    # Check if the update was successful (i.e., rate limit not exceeded)
    return 'Attributes' in response

# app config using requests directly ------------------------------------------------------------------->>
def lambda_handler(event, context):
    try:
        
        print('Processing event...')
        print(f'Event:   {event}')
        print(f'Context: {context}')
        new_event = event_instance(json.loads(event['body']))
        logging.info(f"Received message from use {new_event.first_name} {new_event.last_name} ({new_event.from_id}) : {new_event.text}.")

        # Check rate limit
        if not check_rate_limit(new_event.from_id):
            logging.info('Rate limit exceeded.')
            return {
                'statusCode': 429,
                'body': 'Rate limit exceeded.'
            }

        if new_event.text:
            handle_message(new_event.chat_id, new_event.text, BOT_API_TOKEN)

        print('Response sent.')
        return {
            'statusCode': 200,
            'body': 'Success'
        }
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        logging.error(f'Event: {event}')
        logging.error(f'Context: {context}')
        return {
            'statusCode': 500,
            'body': 'Error'
        }


if __name__ == "__main__":

    # For local testing
    test_event = {
        'body': json.dumps({
            'update_id': 774094673,
            'message': {
                'message_id': 294,
                'from': {
                    'id': 7770769990,
                    'is_bot': False,
                    'first_name': 'Zach',
                    'last_name': 'Wolpe',
                    'language_code': 'en'
                },
                'chat': {
                    'id': 7770769990,
                    'first_name': 'Zach',
                    'last_name': 'Wolpe',
                    'type': 'private'
                },
                'date': 1727346676,
                'text': '/tour '
            }
        })
    }

    lambda_handler(test_event, None)






