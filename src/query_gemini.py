"""
-------------------------------------------------------------------------------------
Query Gemini API

Functions to help query Gemini API.

: zach.wolpe@medibio.com.au
: 19:09:2024
-------------------------------------------------------------------------------------
"""

import google.generativeai as genai
from urllib.parse import quote
import re


def generate_system_prompt(location: str) -> str:
    system_prompt = """you are an experienced, local, tour guide...

        - I want to explore {}.
        - limit the response to 4000 characters.
        - provide the output in Markdown format.
        - Do not use Markdownv2 format as it's not compatible with all platforms.
        - When including links, use standard Markdown link syntax: [link text](URL)
        - Ensure all URLs are properly encoded.
        - For Google Maps links, use the format: https://www.google.com/maps/search/?api=1&query=<encoded location>
        - Provide a number of subheadings with information about the area.
        - iclude google maps links.
        - provide subheadings for:
            - Vegan or vegetarian restaurants.
            - work friendly cafes.
            - artistic cafes.
            - cool attractions.
            - provide a brief history of the area.
            - provide some fun facts about the area.
            - provide statistics about the area.
            - provide any other relevant information.
        - Provide info in a fact like manner, do not ask questions.
        - Structure the response in a way that is easy to read and follow.
        - Don't ask follow up questions.
    """.format(location)

    return system_prompt


def query_gemini_api(system_prompt: str, gemini_version: str = "gemini-1.5-flash") -> str:
    """
    Query Gemini API to generate content based on the system prompt.

    :param system_prompt: str: Query to generate content.
    :return: str: Generated content.
    """

    model = genai.GenerativeModel(gemini_version)
    response = model.generate_content(system_prompt)
    processed_response = process_links(response.text)
    return processed_response


def process_links(content: str) -> str:
    """
    Process the content to ensure links are properly formatted.
    """

    # fix Google Maps links
    def replace_maps_link(match):
        location = match.group(1)
        encoded_location = quote(location)
        return f"https://www.google.com/maps/search/?api=1&query={encoded_location}"

    content = re.sub(r"https://goo\.gl/maps/(\w+)", replace_maps_link, content)

    # Ensure other links are properly encoded
    def replace_link(match):
        text, url = match.groups()
        encoded_url = quote(url, safe=':/?&=')
        return f"[{text}]({encoded_url})"

    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)
    content = re.sub(r'(\[.+?\]\(.+?\))\s*\1', r'\1', content)

    return content
