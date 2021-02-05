from html import escape
from mimetypes import guess_type
from typing import List, Optional

from aiogram import Bot
from aiogram.types import ChatActions, InputFile, InputMediaPhoto, Message
from aiogram.utils.exceptions import BadRequest

from nazurin.models import Caption, File, Image
from nazurin.utils.decorators import chat_action, retry_after
from nazurin.utils.helpers import handleBadRequest

class NazurinBot(Bot):
    send_message = retry_after(Bot.send_message)

    @chat_action(ChatActions.UPLOAD_PHOTO)
    @retry_after
    async def sendPhotos(self,
                         imgs: List[Image],
                         message: Message,
                         caption: Optional[Caption] = Caption()):
        media = list()
        if len(imgs) > 10:
            # TODO
            imgs = imgs[:10]
            await message.reply(
                'Notice: Too many pages, sending only 10 of them')

        caption = caption.text
        if len(caption) > 1024:
            caption = caption[:1024]
            await message.reply('Notice: Caption too long, trimmed')
        caption = escape(caption, quote=False)

        for img in imgs:
            filetype = str(guess_type(img.url)[0])
            if filetype.startswith('image'):
                media.append(InputMediaPhoto(await img.display_url()))  # TODO
            else:
                await message.reply('File is not image, try download option.')
                return
        media[0].caption = caption
        try:
            await message.reply_media_group(media)
        except BadRequest as error:
            await handleBadRequest(message, error)

    @retry_after
    async def sendDocument(self, file: File, chat_id, message_id=None):
        await self.send_document(chat_id,
                                 InputFile(file.path),
                                 reply_to_message_id=message_id)

    @chat_action(ChatActions.UPLOAD_DOCUMENT)
    async def sendDocuments(self,
                            files: List[File],
                            message: Optional[Message] = None,
                            chat_id=None):
        if message:
            message_id = message.message_id
            if not chat_id:
                chat_id = message.chat.id
        else:
            message_id = None  # Sending to channel, no message to reply
        for file in files:
            await self.sendDocument(file, chat_id, message_id)
