import os


def get_bot_token():
    token = os.environ["bot_token"]
    return token


def get_bot_env():
    env = os.environ["bot_env"]
    return env


def get_bot_port():
    port = os.environ["bot_port"]  # 8443
    return port


def get_heroku_app_name():
    return "bd-alert-bot"
