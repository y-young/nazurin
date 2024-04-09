from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from nazurin import bot, dp
from nazurin.utils.exceptions import InvalidCommandUsageError

from .api import Moebooru

moebooru = Moebooru()


@dp.message_handler(
    Command("yandere"),
    args="POST_ID",
    description="View yandere post",
)
async def yandere_view(message: Message, command: CommandObject):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsageError("yandere") from e
    if post_id < 0:
        await message.reply("Invalid post id!")
        return
    illust = await moebooru.site("yande.re").view(post_id)
    await bot.send_illust(illust, message)


@dp.message_handler(
    Command("yandere_download"),
    args="POST_ID",
    description="Download yandere post",
)
async def yandere_download(message: Message, command: CommandObject):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsageError("yandere_download") from e
    if post_id <= 0:
        await message.reply("Invalid post id!")
        return
    illust = await moebooru.site("yande.re").view(post_id)
    await illust.download()
    await bot.send_docs(illust, message)


@dp.message_handler(
    Command("konachan"),
    args="POST_ID",
    description="Download Konachan post",
)
async def konachan_view(message: Message, command: CommandObject):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsageError("konachan") from e
    if post_id < 0:
        await message.reply("Invalid post id!")
        return
    illust = await moebooru.site("konachan.com").view(post_id)
    await bot.send_illust(illust, message)


@dp.message_handler(
    Command("konachan_download"),
    args="POST_ID",
    description="Download Konachan post",
)
async def konachan_download(message: Message, command: CommandObject):
    try:
        post_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsageError("konachan_download") from e
    if post_id <= 0:
        await message.reply("Invalid post id!")
        return
    illust = await moebooru.site("konachan.com").view(post_id)
    await illust.download()
    await bot.send_docs(illust, message)
