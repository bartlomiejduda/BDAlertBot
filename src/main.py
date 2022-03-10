# -*- coding: utf-8 -*-

"""
Copyright © 2021  Bartłomiej Duda
License: GPL-3.0 License
"""

# Program tested on Python 3.7.0
import datetime
from src.env import get_bot_token, get_heroku_app_name, get_bot_port, get_bot_env
from src.logger import get_logger
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
)

VERSION_NUM = "v0.3.0"

logger = get_logger("main")


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        f"Hi! I'm BDAlertBot {VERSION_NUM}.\n"
        "I've been created by Bartlomiej Duda"
        "Type /help to see a list of commands."
    )


def help_reply(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Bot usage:\n"
        "/start - display welcome message\n"
        "/help - display this help message\n"
        "/timer <type> <time> <repeat> - set timer for specified amount of seconds from now\n"
        "  timer types aliases:\n"
        "     s, sec, seconds\n"
        "     m, min, minutes\n"
        "     h, hour, hours\n"
        "     g, gen, generic\n"
        "     e, ext, extended\n"
        "  repeat aliases:\n"
        "     r, rep, repeat\n"
        "  examples:\n"
        "    /timer s 5  <-- sets timer for 5 seconds from now\n"
        "    /timer m 10  <-- sets timer for 10 minutes from now\n"
        "    /timer m 7 r  <-- sets repeating timer every 7 minutes from now\n"
        "    /timer h 1  <-- sets timer for 1 hour from now\n"
        "    /timer g 2 35 17  <--sets timer for 2 hours, 25 minutes and 17 seconds from now\n"
        "    /timer g 3 57 21 r  <-- sets timer to repeat every 3 hours, 57 minutes and 21 seconds\n"
        "    /timer e 21:15 r  <-- sets timer for every day at 21:15"
        "    /timer e 15:17  <-- sets timer to be launched once today ar 15:17\n"
        "/stop - remove all timers from your queue"
        "/list - list all timers"
        "\n"
        "Other methods:\n"
        "/lucky <start> <length> - your lucky number!\n"
        "/lr - left or right?"
    )


def generic_reply(update, context):
    update.message.reply_text(
        "Sorry. I don't understand this command. Type /start or /help for more info."
    )


def alarm(context: CallbackContext) -> None:
    job = context.job
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    alarm_text = "Beep!" + " Time: " + current_time
    context.bot.send_message(job.context, text=alarm_text)


def remove_all_jobs(name: str, context: CallbackContext) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def create_repeating_job(context: CallbackContext, chat_id: int, input_time: int):
    context.job_queue.run_repeating(
        alarm, input_time, context=chat_id, name=str(chat_id)
    )


def create_once_job(context: CallbackContext, chat_id: int, input_time: int):
    context.job_queue.run_once(alarm, input_time, context=chat_id, name=str(chat_id))


def set_timer(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    input_time: int = 0
    logger.info("Setting timer...")
    try:
        input_type = str(context.args[0])

        # CASE 1
        if (
            input_type in ("s", "sec", "seconds")
            or input_type in ("m", "min", "minutes")
            or input_type in ("h", "hour", "hours")
        ):
            input_time = int(context.args[1])

            if input_time < 0:
                update.message.reply_text("Sorry we can not go back to future!")
                return

            if input_type in ("m", "min", "minutes"):
                input_time = input_time * 60
            if input_type in ("h", "hour", "hours"):
                input_time = input_time * 60 * 60

            repeat = None
            try:
                repeat = str(context.args[2])
            except (IndexError, ValueError):
                pass

            if repeat in ("r", "rep", "repeat"):
                create_repeating_job(context, chat_id, input_time)
            else:
                create_once_job(context, chat_id, input_time)

        # CASE 2
        elif input_type in ("g", "gen", "generic"):
            input_h = int(context.args[1])
            input_m = int(context.args[2])
            input_s = int(context.args[3])

            input_time = 0
            input_time += input_h * 60 * 60
            input_time += input_m * 60
            input_time += input_s

            repeat = None
            try:
                repeat = str(context.args[4])
            except (IndexError, ValueError):
                pass

            if repeat in ("r", "rep", "repeat"):
                create_repeating_job(context, chat_id, input_time)
            else:
                create_once_job(context, chat_id, input_time)

        else:
            text = "Wrong timer type! See /help for more info."
            update.message.reply_text(text)
            return

        text = "Timer successfully set!"
        update.message.reply_text(text)

    except (IndexError, ValueError) as error:
        logger.error("Error: %s", error)
        text = "Wrong arguments! See /help for more info."
        update.message.reply_text(text)


def stop(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    job_removed = remove_all_jobs(str(chat_id), context)
    text = (
        "All timers have been cancelled!"
        if job_removed
        else "You have no active timer."
    )
    update.message.reply_text(text)


def main() -> None:
    logger.info("Main start...")
    updater = Updater(get_bot_token())

    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_reply))
    dispatcher.add_handler(CommandHandler("timer", set_timer))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, generic_reply)
    )

    heroku_app_name = get_heroku_app_name()
    env = get_bot_env()

    if env == "DEV":
        logger.info("Starting bot on DEV...")
        updater.start_polling()
    elif env == "PROD":
        logger.info("Starting bot on PROD...")
        updater.start_webhook(
            listen="0.0.0.0",
            port=get_bot_port(),
            url_path=get_bot_token(),
            webhook_url=f"https://{heroku_app_name}.herokuapp.com/" + get_bot_token(),
        )
    else:
        raise Exception("Environment not set properly!")

    updater.idle()
    logger.info("End of main...")


if __name__ == "__main__":
    main()
