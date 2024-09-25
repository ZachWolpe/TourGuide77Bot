"""
-------------------------------------------------------------------------------------
Telegram API Logic

Functions to handle async Telegram API calls.

: zach.wolpe@medibio.com.au
: 20:09:2024
-------------------------------------------------------------------------------------
"""

from query_gemini import query_gemini_api, generate_system_prompt
from telegram.ext import (ContextTypes)
from dotenv import load_dotenv
from telegram import Update
import numpy as np
import logging
import os
import re

from telegram_api_helpers import (
    BotConfig,
    BotMessages,
    split_message, 
    escape_special_chars,
    chunk_response,
    write_response_to_text_file)


# load env --------------------------------------------------------------------------------------------->>
load_dotenv()
BOT_USERNAME = os.getenv("BOT_USERNAME")
# load env --------------------------------------------------------------------------------------------->>


def handle_response(text: str) -> str:
    """
    Respond to general messages.
    """
    lower_case_text: str = text.lower()

    if "hello" in lower_case_text.lower():
        return "Hello!"

    _response = np.random.choice(BotMessages.random_response_1, BotMessages.random_response_2, BotMessages.random_response_3, BotMessages.random_response_4)

    if "help" in lower_case_text.lower():
        return BotMessages.helper_message
    return _response


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(BotMessages.start_message, parse_mode=BotConfig.PARSE_MODE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Which city are you interesting in learning about?", parse_mode=BotConfig.PARSE_MODE)


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Coming soon...", parse_mode=BotConfig.PARSE_MODE)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Update {update} caused error {context.error}")


async def test_google_map_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://goo\.gl/maps/4GRcDoxK1jP1KyrN6"
    msg = f"Here is a link to Google Maps: {url}"
    await update.message.reply_text(msg, parse_mode=BotConfig.PARSE_MODE)


async def test_debug_messsage_format_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('test-response.txt', 'r') as f:
        fake_message = f.read()
    await update.message.reply_text(fake_message, parse_mode=BotConfig.PARSE_MODE)


async def travel_tips_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Return travel tips, broken into segments for exceed the Telegram API limit.
    """

    LOCATION = ''.join(context.args)
    if isinstance(LOCATION, tuple) or isinstance(LOCATION, list):
        LOCATION = LOCATION[0]

    if not LOCATION:
        return await update.message.reply_text(BotMessages.location_not_provided_error)
    logging.info('> Querying location: ', LOCATION)

    # querying gemini api
    system_prompt = generate_system_prompt(LOCATION)  # generate system prompt
    text_response = query_gemini_api(system_prompt)  # query gemini api

    # change heading type
    # text_response = re.sub(r'\n#+\s', '\n ', text_response)

    # write to file
    write_response_to_text_file(text_response, 'response.txt')

    # send messages in chucks
    for _i, _msg in chunk_response(text_response):
        # print('Chunk len:   ', len(_msg))
        # print('Chunk # :    ', _i)
        await update.message.reply_text(_msg, parse_mode=BotConfig.PARSE_MODE)
    logging.info('Response complete.')


# handle messages
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    user: str = update.message.chat.username
    user_id: int = update.message.chat.id

    logging.info(f"Received message from use {user_id} ({user}) : {text}.")

    if message_type == 'group':
        # if in a group chat: only respond to messages that mention the bot
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response = handle_response(new_text)
        else:
            return

    else:
        # private chat
        response = handle_response(text)

    logging.info(f"Sending response to user {user_id} ({user}): {response}")
    await update.message.reply_text(response, parse_mode=BotConfig.PARSE_MODE)