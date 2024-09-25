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
: 20:09:2024
-------------------------------------------------------------------------------------
"""

import google.generativeai as genai
from dotenv import load_dotenv
import logging
import os

from telegram.ext import (
    Application,
    CommandHandler,
    filters,
    MessageHandler)

# from query_gemini import query_gemini_api, generate_system_prompt
from telegram_api_commands import (
    start_command,
    help_command,
    custom_command,
    travel_tips_command,
    error,
    # test_google_map_command,
    # test_debug_messsage_format_command,
    message_handler)


# load env --------------------------------------------------------------------------------------------->>
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv()
BOT_API_TOKEN: str = os.getenv("BOT_API_TOKEN")
BOT_USERNAME: str = os.getenv("BOT_USERNAME")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# load env --------------------------------------------------------------------------------------------->>


def lambda_handler(event, context):
    try:
        logging.info(' > Stage 1: Application built...')
        app = Application.builder().token(BOT_API_TOKEN).build()

        # Commands
        app.add_handler(CommandHandler("start",                 start_command))
        app.add_handler(CommandHandler("help",                  help_command))
        app.add_handler(CommandHandler("custom",                custom_command))
        app.add_handler(CommandHandler("travel_tips",           travel_tips_command))
        # app.add_handler(CommandHandler("test_google_map",       test_google_map_command))
        # app.add_handler(CommandHandler("test_message_format",   test_debug_messsage_format_command))

        # Messages
        app.add_handler(MessageHandler(filters.TEXT, lambda update, context: message_handler(update, context, bot_username=BOT_USERNAME)))

        # Error
        app.add_error_handler(error)

        # Start the bot
        logging.info("App stared. Polling...")
        app.run_polling(poll_interval=1)
    except Exception as e:
        logging.error('An error occurred: ', e)
        return 1


if __name__ == "__main__":
    lambda_handler(None, None)