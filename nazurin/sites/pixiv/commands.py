from re import Match

from aiogram.dispatcher.filters import Command, Regexp
from aiogram.types import Message

from nazurin import bot, dp

from .api import Pixiv
from .config import PixivPrivacy

pixiv = Pixiv()

@dp.message_handler(Command(['pixiv']))
async def pixiv_view(message: Message, command: Command.CommandObj):
    try:
        artwork_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply('Usage: /pixiv ARTWORK_ID')
        return
    if artwork_id < 0:
        await message.reply('Invalid artwork id!')
        return
    illust = await pixiv.view(artwork_id)
    await bot.send_illust(illust, message)

@dp.message_handler(Command(['pixiv_download']))
async def pixiv_download(message: Message, command: Command.CommandObj):
    try:
        artwork_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply('Usage: /pixiv_download ARTWORK_ID')
        return
    if artwork_id < 0:
        await message.reply('Invalid artwork id!')
        return
    illust = await pixiv.view(artwork_id)
    await illust.download()
    await bot.send_docs(illust, message)

@dp.message_handler(Command(['pixiv_bookmark', 'pixiv_bookmark_private']))
async def pixiv_bookmark(message: Message, command: Command.CommandObj):
    try:
        artwork_id = int(command.args)
    except (IndexError, ValueError, TypeError):
        await message.reply('Usage: /pixiv_bookmark ARTWORK_ID')
        return
    if artwork_id < 0:
        await message.reply('Invalid artwork id!')
        return
    privacy = PixivPrivacy.PUBLIC
    if command.command == 'pixiv_bookmark_private':
        privacy = PixivPrivacy.PRIVATE
    await pixiv.bookmark(artwork_id, privacy)
    await message.reply('Done!')

@dp.message_handler(Regexp(r'(?:www\.)?pixiv\.net/(?:users|u)/(\d+)'))
async def pixiv_follow(message: Message, regexp: Match):
    user_id = int(regexp.group(1))
    await pixiv.follow_user(user_id)
    await message.reply(f'Successfully followed user {user_id}.')
