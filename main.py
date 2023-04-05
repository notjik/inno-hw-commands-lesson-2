"""
Добавить в бота реализацию работы с SQLite.
"""
# *You need to download: "aiogram", "python-dotenv"*
# *You need to add a token, host, path to the environment variable*

# Imports for working with a bot
import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, filters
from aiogram.utils import executor, exceptions
from dotenv import load_dotenv
from database import db_session, users, blacklist
from utils.loggers import logger_message, logger_status, logger_database_engine
from utils.custom_filters import IsBanword, InBlackList
from utils.menu import set_starting_commands

# Loading environment variables
load_dotenv()

# Unloading local variables and initializing the bot
try:
    WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
    WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
    WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH
    WEBAPP_HOST = os.getenv('WEBAPP_HOST')
    WEBAPP_PORT = os.getenv('WEBAPP_PORT')
    bot = Bot(token=os.getenv('TOKEN'))
except TypeError as e:
    exit('Create local variables: {}'.format(e))
dispatcher = Dispatcher(bot)


async def startup(callback):
    """
    Logging the launch of the bot

    :param callback: dispatcher object
    :return: None
    """
    db_session.global_init("data/aiogram_bot.db")
    await bot.set_webhook(WEBHOOK_URL)
    me = await callback.bot.get_me()
    extra = {
        'bot': me.username,
        'bot_id': me.id,
    }
    logger_status.info('has been successfully launched.', extra=extra)


async def shutdown(callback):
    """
    Logging off the bot

    :param callback: dispatcher object
    :return: None
    """
    logger_database_engine.info('Closing the connection due to program shutdown.')
    await bot.delete_webhook()
    me = await callback.bot.get_me()
    extra = {
        'bot': me.username,
        'bot_id': me.id,
    }
    logger_status.info('is disabled.', extra=extra)


@dispatcher.message_handler(InBlackList())
async def in_blacklist(msg: types.Message):
    """
    The help message of the bot

    :param msg: message object
    :return: answer
    """
    extra = {
        'user': msg.from_user.username,
        'user_id': msg.from_user.id,
        'content_type': 'writes while on the blacklist'
    }
    logger_message.warning(msg, extra=extra)


@dispatcher.message_handler(IsBanword())
async def add_to_blacklist(msg: types.Message):
    """
    The help message of the bot

    :param msg: message object
    :return: answer
    """
    db_sess = db_session.create_session()
    q = db_sess.query(blacklist.Blacklist).filter_by(user_id=msg.from_user.id)
    if not q.all():
        blcklst = blacklist.Blacklist(user_id=msg.from_user.id)
        db_sess.add(blcklst)
        db_sess.commit()
    await msg.answer("I'm adding you to the blacklist!😠")  # Request with a message to the user
    extra = {
        'user': msg.from_user.username,
        'user_id': msg.from_user.id,
        'content_type': 'added to the blacklist'
    }
    logger_message.info(msg, extra=extra)


@dispatcher.message_handler(filters.CommandStart())
async def start_message(msg: types.Message):
    """
    The starting message of the bot

    :param msg: message object
    :return: answer
    """
    db_sess = db_session.create_session()
    q = db_sess.query(users.Users).filter_by(user_id=msg.from_user.id)
    if q.all():
        q.update({'firstname': msg.from_user.first_name,
                  'lastname': msg.from_user.last_name,
                  'username': msg.from_user.username})
    else:
        user = users.Users(user_id=msg.from_user.id,
                           firstname=msg.from_user.first_name,
                           lastname=msg.from_user.last_name,
                           username=msg.from_user.username)
        db_sess.add(user)
    db_sess.commit()
    await msg.answer('Hi! Welcome to the bot from the homework of Innopolis University. \n'
                     'This is an echo bot.')  # Request with a message to the user
    await set_starting_commands(bot, msg.chat.id)
    extra = {
        'user': msg.from_user.username,
        'user_id': msg.from_user.id,
        'content_type': '/start'
    }
    logger_message.info(msg, extra=extra)


@dispatcher.message_handler(filters.CommandHelp())
async def help_message(msg: types.Message):
    """
    The help message of the bot

    :param msg: message object
    :return: answer
    """
    await msg.answer("Just send me a message and I'll repeat it!")  # Request with a message to the user
    extra = {
        'user': msg.from_user.username,
        'user_id': msg.from_user.id,
        'content_type': '/help'
    }
    logger_message.info(msg, extra=extra)


@dispatcher.message_handler(content_types=['any'])
async def echo(msg: types.Message):
    """
    Echo function.

    :param msg: message object
    :return: send message
    """
    await bot.copy_message(chat_id=msg.chat.id,
                           from_chat_id=msg.chat.id,
                           message_id=msg.message_id)  # Request to copy a message
    extra = {
        'user': msg.from_user.username,
        'user_id': msg.from_user.id,
        'content_type': msg.content_type
    }
    logger_message.info(msg, extra=extra)


@dispatcher.errors_handler(exception=exceptions.BotBlocked)
async def except_bot_blocked(update: types.Update, exception: exceptions.BotBlocked):
    extra = {
        'user': update.message.from_user.username,
        'user_id': update.message.from_user.id,
        'content_type': 'the bot to the ban'
    }
    logger_message.warning(update.message, extra=extra)
    return True


# Entry point
if __name__ == '__main__':
    executor.start_webhook(
        dispatcher=dispatcher,
        webhook_path=WEBHOOK_PATH,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
        on_startup=startup,
        on_shutdown=shutdown,
        skip_updates=True,
    )  # Launching webhook
