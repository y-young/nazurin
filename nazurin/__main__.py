import asyncio
import os
import shutil
import traceback
from textwrap import dedent

from aiogram.dispatcher.filters import Command, IDFilter
from aiogram.types import ChatActions, Message, Update
from aiogram.utils.exceptions import TelegramAPIError
from aiohttp import ClientResponseError

from nazurin import config, dp
from nazurin.utils import logger
from nazurin.utils.decorators import Cache, chat_action
from nazurin.utils.exceptions import InvalidCommandUsage, NazurinError
from nazurin.utils.helpers import format_error


@dp.message_handler(commands=["start"], description="Get help")
@chat_action(ChatActions.TYPING)
async def start(message: Message):
    await show_help(message, None)


@dp.message_handler(
    commands=["help"],
    args="[COMMAND]",
    description="Get help of all commands or a specific command",
)
@chat_action(ChatActions.TYPING)
async def show_help(message: Message, command: Command.CommandObj):
    if command and command.args:
        help_text = dp.commands.help(command.args)
        await message.reply(help_text or "Command not found.")
        return
    await message.reply(
        dedent(
            """
            小さな小さな賢将, can help you collect images from various sites.

            <b>Commands:</b>
            """
        )
        + dp.commands.help_text()
        + dedent(
            """

            PS: Send a URL of supported sites to collect image(s)
            """
        ),
    )


@dp.message_handler(commands=["ping"], description="Pong")
@chat_action(ChatActions.TYPING)
async def ping(message: Message):
    await message.reply("Pong!")


@dp.message_handler(
    IDFilter(config.ADMIN_ID),
    commands=["set_commands"],
    description="Set commands",
)
async def set_commands(message: Message):
    await dp.bot.set_my_commands(list(dp.commands.list()))
    await message.reply("Commands set successfully.")


@dp.message_handler(
    IDFilter(config.ADMIN_ID),
    commands=["clear_cache"],
    description="Clear cache",
)
async def clear_cache(message: Message):
    try:
        if os.path.exists(config.TEMP_DIR):
            shutil.rmtree(config.TEMP_DIR)
        Cache.clear()
        await message.reply("Cache cleared successfully.")
    except PermissionError:
        await message.reply("Permission denied.")
    except OSError as error:
        await message.reply(error.strerror)


@dp.errors_handler()
async def on_error(update: Update, exception: Exception):
    message = update.message
    try:
        raise exception
    except InvalidCommandUsage as error:
        await message.reply(dp.commands.help(error.command))
    except ClientResponseError as error:
        traceback.print_exc()
        await message.reply(f"Response Error: {error.status} {error.message}")
    except NazurinError as error:
        await message.reply(error.msg)
    except asyncio.TimeoutError:
        traceback.print_exc()
        await message.reply("Error: Timeout, please try again.")
    except Exception as error:  # pylint: disable=broad-except
        logger.exception("Update {} caused {}: {}", update, type(error), error)
        if not isinstance(error, TelegramAPIError):
            await message.reply(f"Error: {format_error(error)}")

    return True


def main():
    dp.start()


if __name__ == "__main__":
    main()
