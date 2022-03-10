# BDAlertBot
Telegram bot for sending customized alerts to users.

Contact **[@bduda_admin_bot](https://t.me/bduda_admin_bot)** on Telegram to see this bot in action.

Type **/help** in message window to get a list of commands.



<img src="src\data\img\usage.gif">


# Building on Windows

1. Install  **[Python 3.7.0](https://www.python.org/downloads/release/python-370/)**
2. Install **[PyCharm 2021.3.2 (Community Edition)](https://www.jetbrains.com/pycharm/download/#section=windows)**
3. Create virtualenv and activate it
   - python3 -m venv \path\to\new\virtual\environment
   - .\venv\Scripts\activate.bat
4. Install all libraries from requirements.txt
   - pip3 install -r requirements.txt
5. Set all required environment variables (see env.py for more info)
6. Run the src\main.py file


# Deploying on Heroku

This app is designed to be deployed on **[heroku.com](https://heroku.com)** cloud platform.

// TODO