# -*- coding: utf-8 -*-

"""
Copyright © 2021  Bartłomiej Duda
License: GPL-3.0 License
"""

# Program tested on Python 3.7.0
from src.env import get_bot_token, get_heroku_app_name, get_bot_port, get_bot_env
from src.logger import get_logger
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

VERSION_NUM = "v0.2.5"

logger = get_logger("main")


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hi! I\'m BDAlertBot {VERSION_NUM}.\n'
                              'I\'ve been created by Bartlomiej Duda'
                              'Type /help to see a list of commands.')


def help_reply(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bot usage:\n'
                              '/start - display welcome message\n'
                              '/help - display this help message\n'
                              '/timer_s <seconds> - set timer for specified amount of seconds from now\n'
                              '/timer_m <minutes> - set timer for specified amount of minutes from now\n'
                              '/timer_h <hours> - - set timer for specified amount of hours from now\n'
                              '/timer_g <hours> <minutes> <seconds> - set generic timer\n'
                              '/timer_d <hour>:<minutes> - to set alert for every day at the same hour\n'
                              '\n'
                              'Other methods:\n'
                              '/lucky <start> <length> - your lucky number!\n'
                              '/lr - left or right?')


def generic_reply(update, context):
    update.message.reply_text('Sorry. I don\'t understand this command. Type /start or /help for more info.')


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

        text = 'Timer successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)


def main() -> None:

    logger.info("Main start...")
    updater = Updater(get_bot_token())

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_reply))
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("unset", unset))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, generic_reply))

    heroku_app_name = get_heroku_app_name()
    env = get_bot_env()

    if env == "DEV":
        logger.info("Starting bot on DEV...")
        updater.start_polling()
    elif env == "PROD":
        logger.info("Starting bot on PROD...")
        updater.start_webhook(listen="0.0.0.0",
                              port=get_bot_port(),
                              url_path=get_bot_token(),
                              webhook_url=f"https://{heroku_app_name}.herokuapp.com/" + get_bot_token())
    else:
        raise Exception("Environment not set properly!")

    updater.idle()
    logger.info("End of main...")


if __name__ == '__main__':
    main()