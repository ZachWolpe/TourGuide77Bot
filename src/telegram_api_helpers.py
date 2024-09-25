"""
-------------------------------------------------------------------------------------
Telegram API Helpers

Functions to help parse and transform the Telegram API responses.

: zach.wolpe@medibio.com.au
: 20:09:2024
-------------------------------------------------------------------------------------
"""

import logging
import re


class BotConfig:
    PARSE_MODE = 'MarkdownV2'
    SPECIAL_CHARS = ['\\', '_', '*', '[', ']', '(', ')', '~', '`', '>', '<', '&', '#', '+', '-', '=', '|', '{', '}', '.', '!']


class BotMessages:
    helper_message = 'Please provide a location argument after /travel_tips <arg> to form a valid query. For example: \n  \"/travel_tips Harajuku\".'
    location_not_provided_error = 'Please provide a location argument after /travel_tips <arg> to form a valid query. For example: \n  \"/travel_tips Harajuku\".'
    start_message = """
        Hello! I am TourGuide77Bot. I can help you with your travel plans. \n{}.
        """.format(helper_message)
    random_response_1 = "404 not found! Try asking for \/travel_tips..."
    random_response_2 = "Hmmm not sure what you want..."
    random_response_3 = """
         _  _    ___  _  _     _   _       _     _____                     _         
        | || |  / _ \| || |   | \ | | ___ | |_  |  ___|__  _   _ _ __   __| |       
        | || |_| | | | || |_  |  \| |/ _ \| __| | |_ / _ \| | | | '_ \ / _` |      
        |__   _| |_| |__   _| | |\  | (_) | |_  |  _| (_) | |_| | | | | (_| |_ _ _ _ 
           |_|  \___/   |_|   |_| \_|\___/ \__| |_|  \___/ \__,_|_| |_|\__,_(_|_|_|_)
        """
    random_response_4 = "I'm sorry, I don't understand that command. Please type /help to get started."


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

        # debugging
        # _msg = escape_special_chars(_message, [i for i in SPECIAL_CHARS if i not in ['*', '_']])
        # _msg = escape_special_chars(_message, [i for i in ['#', '*', '_', '+']])
        _msg = escape_special_chars(_message, BotConfig.SPECIAL_CHARS)

        yield _i, _msg


def write_response_to_text_file(text_response: str, filename: str = 'response.txt'):
    with open(filename, 'w') as f:
        f.write(text_response)
