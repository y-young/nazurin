from re import Match

from aiogram import F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from nazurin import bot, dp
from nazurin.utils.exceptions import InvalidCommandUsageError

from .api import Pixiv
from .config import PixivPrivacy

pixiv = Pixiv()


@dp.message_handler(
    Command("pixiv"),
    args="ARTWORK_ID",
    description="View Pixiv artwork",
)
async def pixiv_view(message: Message, command: CommandObject):
    try:
        artwork_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsageError("pixiv") from e
    if artwork_id < 0:
        await message.reply("Invalid artwork id!")
        return
    illust = await pixiv.view(artwork_id)
    await bot.send_illust(illust, message)


@dp.message_handler(
    Command("pixiv_download"),
    args="ARTWORK_ID",
    description="Download Pixiv artwork",
)
async def pixiv_download(message: Message, command: CommandObject):
    try:
        artwork_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsageError("pixiv_download") from e
    if artwork_id < 0:
        await message.reply("Invalid artwork id!")
        return
    illust = await pixiv.view(artwork_id)
    await illust.download()
    await bot.send_docs(illust, message)


@dp.message_handler(
    Command("pixiv_bookmark", "pixiv_bookmark_private"),
    args="ARTWORK_ID",
    description="Bookmark Pixiv artwork",
)
async def pixiv_bookmark(message: Message, command: CommandObject):
    try:
        artwork_id = int(command.args)
    except (IndexError, ValueError, TypeError) as e:
        raise InvalidCommandUsageError("pixiv_bookmark") from e
    if artwork_id < 0:
        await message.reply("Invalid artwork id!")
        return
    privacy = PixivPrivacy.PUBLIC
    if command.command == "pixiv_bookmark_private":
        privacy = PixivPrivacy.PRIVATE
    await pixiv.bookmark(artwork_id, privacy)
    await message.reply("Done!")


@dp.message_handler(F.text.regexp(r"(?:www\.)?pixiv\.net/(?:users|u)/(\d+)"))
async def pixiv_follow(message: Message, regexp: Match):
    user_id = int(regexp.group(1))
    await pixiv.follow_user(user_id)
    await message.reply(f"Successfully followed user {user_id}.")
