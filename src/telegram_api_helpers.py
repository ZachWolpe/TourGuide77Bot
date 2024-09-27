"""
-------------------------------------------------------------------------------------
Telegram API Helpers

Functions to help parse and transform the Telegram API responses.

: zach.wolpe@medibio.com.au
: 20:09:2024
-------------------------------------------------------------------------------------
"""
from query_gemini import query_gemini_api, generate_system_prompt
import numpy as np
import requests
import logging
import re


class BotConfig:
    PARSE_MODE = 'MarkdownV2'
    SPECIAL_CHARS = ['\\', '_', '*', '[', ']', '(', ')', '~', '`', '>', '<', '&', '#', '+', '-', '=', '|', '{', '}', '.', '!']


class BotMessages:
    TRAVEL_KEY = '/travel'
    helper_message = f"Please provide a location argument after /travel <arg> to form a valid query. For example: \n  \'{TRAVEL_KEY} Harajuku\'."
    location_not_provided_error = f"Please provide a location argument after /travel <arg> to form a valid query. For example: \n  \'{TRAVEL_KEY} Harajuku\'."
    about_message = """
    -------------------------------------------------------------------------------------
    About TourGuide77Bot
    ---------------------

    I exist to kickstart any travel journey, ask me about any city and I'll give you the lowdown on the best places to visit, eat, and explore.

    More advanced features coming soon...

    : author        : zach wolpe
    : email         : zach.wolpe@medibio.com.au
    : release date  : 27 Sep 2024
    -------------------------------------------------------------------------------------
    """
    start_message = """
        Hello! I am TourGuide77Bot - your personal tour guide. I can help you with your travel plans. \n{}.
        """.format(helper_message)
    random_response_1 = f"404 not found! Try asking for {TRAVEL_KEY}..."
    random_response_2 = "Hmmm not sure what you want..."
    random_response_3 = "I'm sorry, I don't understand that command. Please type /help to get started."
    random_response_4 = """
         _  _    ___  _  _     _   _       _     _____                     _         
        | || |  / _ \| || |   | \ | | ___ | |_  |  ___|__  _   _ _ __   __| |       
        | || |_| | | | || |_  |  \| |/ _ \| __| | |_ / _ \| | | | '_ \ / _` |      
        |__   _| |_| |__   _| | |\  | (_) | |_  |  _| (_) | |_| | | | | (_| |_ _ _ _ 
           |_|  \___/   |_|   |_| \_|\___/ \__| |_|  \___/ \__,_|_| |_|\__,_(_|_|_|_)
        """

    @staticmethod
    def sample_random_response():
        return np.random.choice([BotMessages.random_response_1, BotMessages.random_response_2, BotMessages.random_response_3, BotMessages.random_response_4])


class event_instance:
    """
    Extract event instance from the Telegram API response.
    """
    def __init__(self, event):
        self.update_id = event['update_id']
        self.message_id = event['message']['message_id']
        self.from_id = event['message']['from']['id']
        self.is_bot = event['message']['from'].get('is_bot', False)
        self.first_name = event['message']['from'].get('first_name', '')
        self.last_name = event['message']['from'].get('last_name', '')
        self.language_code = event['message']['from'].get('language_code', '')
        self.chat_id = event['message']['chat']['id']
        self.chat_first_name = event['message']['chat'].get('first_name', '')
        self.chat_last_name = event['message']['chat'].get('last_name', '')
        self.chat_type = event['message']['chat'].get('type', '')
        self.date = event['message']['date']
        self.text = event['message'].get('text', '')


def split_message(content: str) -> list:
    """
    Split message into chunks that are less than the Telegram API limit.
    """
    # sections = re.split(r'\n#+\s', content)
    sections = re.split(r'\n#+\s', content)

    sections = [section.strip() for section in sections]
    return sections


def escape_special_chars(text: str, SPECIAL_CHARS=BotConfig.SPECIAL_CHARS) -> str:
    for char in SPECIAL_CHARS:
        text = text.replace(char, f'\\{char}')
    return text


def chunk_response(text_response: str):
    logging.info('Sending response in chunks...')
    for _i, _message in enumerate(split_message(text_response)):
        # remove '###' from headings and '*'
        _msg = re.sub(r'\n#+\s', '\n ', _message)
        _msg = re.sub(r'\n\*\s', '\n ', _msg)
        _msg = escape_special_chars(_message, BotConfig.SPECIAL_CHARS)

        yield _i, _msg


def write_response_to_text_file(text_response: str, filename: str = 'response.txt'):
    with open(filename, 'w') as f:
        f.write(text_response)


def send_message(chat_id, text, BOT_API_TOKEN):
    url = f"https://api.telegram.org/bot{BOT_API_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": BotConfig.PARSE_MODE
    }
    print(f'Sending message (chat_id:{chat_id}) : {text}')
    response = requests.post(url, json=payload)
    return response.json()


def bot_query_gemini_api(text: str):

    system_prompt = generate_system_prompt(text)  # generate system prompt
    text_response = query_gemini_api(system_prompt, _process_links=True)  # query gemini api

    # write to file
    write_response_to_text_file(text_response, 'response.txt')

    return text_response


class BotCommands:
    message_handler_map = {
        '/start': BotMessages.start_message,
        '/help': BotMessages.helper_message,
        '/h': BotMessages.helper_message,
        '/?': BotMessages.helper_message,
        '/about': BotMessages.about_message,
        '/tour': bot_query_gemini_api,
    }


def handle_message(chat_id, text, BOT_API_TOKEN):
    """
    Handle incoming messages from the Telegram API.
    """

    # map message to response
    start_of_message = text.lower().strip().split(' ')[0]
    return_message = BotCommands.message_handler_map.get(start_of_message, BotMessages.sample_random_response())

    print('> start_of_message: ', start_of_message)
    print('> return_message:   ', return_message)

    if not isinstance(return_message, str):
        text_response = return_message(text)

        # send messages in chucks to avoide exceeding the Telegram API limit
        for _i, _msg in chunk_response(text_response):
            send_message(chat_id, _msg, BOT_API_TOKEN)

        return True

    send_message(chat_id, return_message, BOT_API_TOKEN)
    return True
