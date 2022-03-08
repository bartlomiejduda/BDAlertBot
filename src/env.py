import os


def get_bot_token() -> str:
    token = os.environ["bot_token"]
    return token


def get_bot_env() -> str:
    env = os.environ["bot_env"]
    return env


def get_bot_port() -> int:
    port = int(os.environ.get('PORT'))  # Port is given by Heroku
    return port


def get_heroku_app_name() -> str:
    return "bd-alert-bot"
