from html import escape
from mimetypes import guess_type
from typing import List, Optional

from aiogram import Bot
from aiogram.types import ChatActions, InputFile, InputMediaPhoto, Message
from aiogram.utils.exceptions import BadRequest

from nazurin import config
from nazurin.models import Caption, File, Image
from nazurin.sites import SiteManager
from nazurin.storage import Storage
from nazurin.utils import logger
from nazurin.utils.decorators import chat_action, retry_after
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import handleBadRequest

class NazurinBot(Bot):
    send_message = retry_after(Bot.send_message)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sites = SiteManager()
        self.storage = Storage()

    def init(self):
        self.sites.load()
        self.storage.load()

    @chat_action(ChatActions.UPLOAD_PHOTO)
    @retry_after
    async def sendSingleGroup(self, imgs: List[Image], message: Message,
                              caption: str):
        media = list()
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

    async def sendPhotos(self,
                         imgs: List[Image],
                         message: Message,
                         caption: Optional[Caption] = Caption()):
        caption = caption.text
        if len(caption) > 1024:
            caption = caption[:1024]
            await message.reply('Notice: Caption too long, trimmed')
        caption = escape(caption, quote=False)

        groups = list()
        while imgs:
            groups.append(imgs[:10])
            imgs = imgs[10:]

        for group in groups:
            await self.sendSingleGroup(group, message, caption)

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

    async def update_collection(self,
                                urls: List[str],
                                message: Optional[Message] = None):
        result = self.sites.match(urls)
        if not result:
            raise NazurinError('No source matched')
        logger.info('Collection update: site=%s, match=%s', result['site'],
                    result['match'].groups())
        # Forward to gallery & Save to album
        if message:  # TODO
            await message.forward(config.GALLERY_ID)

        imgs = await self.sites.handle_update(result)
        await self.storage.store(imgs)
        return True
