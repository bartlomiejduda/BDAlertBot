# -*- coding: utf-8 -*-

"""
Copyright © 2021  Bartłomiej Duda
License: GPL-3.0 License
"""

# Program tested on Python 3.7.0
import os

from src.logger import get_logger
import requests


VERSION_NUM = "v0.1.0"

logger = get_logger("main")


def get_api_link():
    return "https://api.telegram.org/bot"


def get_token():
    token = os.environ["telegram_token"]
    return token


def get_response(method_name, params=""):
    api_link = get_api_link()
    token = get_token()
    response = requests.get(f"{api_link}{token}/{method_name}{params}")
    logger.info("method: %s, response.text: %s", method_name, response.text)
    return response


def main():
    """
    Main function of this program.
    """

    logger.info("Starting main...")



    status = get_response("getMe")

    if not status:
        logger.error("Request failed!")
        raise Exception("Request failed!")



    # params = "?chat_id=@alert_bot_test_1&text=aaa"
    # get_response("sendMessage", params)


    updates = get_response("getUpdates")

    newest_update_id = updates.json().get("result")[0].get("update_id") + 1


    # CLEAR ALL UPDATES
    # newest_update_id = 886270911
    params = f"?offset={newest_update_id}"
    get_response("getUpdates", params)



    logger.info("End of main...")


if __name__ == "__main__":
    main()
