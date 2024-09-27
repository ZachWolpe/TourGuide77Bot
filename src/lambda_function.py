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

import google.generativeai as genai
from dotenv import load_dotenv
import logging
import json
import os

from telegram_api_helpers import (event_instance, handle_message)


# load env --------------------------------------------------------------------------------------------->>
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv()
BOT_API_TOKEN: str = os.getenv("BOT_API_TOKEN")
BOT_USERNAME: str = os.getenv("BOT_USERNAME")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# load env --------------------------------------------------------------------------------------------->>


# app config using requests directly ------------------------------------------------------------------->>
def lambda_handler(event, context):
    try:
        print('Processing event...')
        new_event = event_instance(json.loads(event['body']))
        print(f"Received message from use {new_event.first_name} {new_event.last_name} ({new_event.from_id}) : {new_event.text}.")

        if new_event.text:
            handle_message(new_event.chat_id, new_event.text, BOT_API_TOKEN)

        print('Response sent.')
        return {
            'statusCode': 200,
            'body': 'Success'
        }
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
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
                'text': '/tour Sydney'
            }
        })
    }

    lambda_handler(test_event, None)






