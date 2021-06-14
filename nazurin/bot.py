import asyncio
from typing import List, Optional

from aiogram import Bot
from aiogram.types import ChatActions, InputFile, InputMediaPhoto, Message
from aiogram.types.message import ParseMode
from aiogram.utils.exceptions import BadRequest

from nazurin import config
from nazurin.models import File, Illust, Image, Ugoira
from nazurin.sites import SiteManager
from nazurin.storage import Storage
from nazurin.utils import logger
from nazurin.utils.decorators import retry_after
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import handleBadRequest, sanitizeCaption

class NazurinBot(Bot):
    send_message = retry_after(Bot.send_message)

    def __init__(self, *args, **kwargs):
        super().__init__(parse_mode=ParseMode.HTML, *args, **kwargs)
        self.sites = SiteManager()
        self.storage = Storage()

    def init(self):
        self.sites.load()
        self.storage.load()

    @retry_after
    async def sendSingleGroup(self,
                              imgs: List[Image],
                              caption: str,
                              chat_id: int,
                              reply_to: Optional[int] = None):
        await self.send_chat_action(chat_id, ChatActions.UPLOAD_PHOTO)
        media = list()
        for img in imgs:
            media.append(InputMediaPhoto(await img.display_url()))  # TODO
        media[0].caption = caption
        await self.send_media_group(chat_id,
                                    media,
                                    reply_to_message_id=reply_to)

    async def sendPhotos(self,
                         illust: Illust,
                         chat_id: int,
                         reply_to: Optional[int] = None):
        caption = sanitizeCaption(illust.caption)
        groups = list()
        imgs = illust.images
        if len(imgs) == 0:
            raise NazurinError('No image to send, try download option.')

        while imgs:
            groups.append(imgs[:10])
            imgs = imgs[10:]

        for group in groups:
            await self.sendSingleGroup(group, caption, chat_id, reply_to)

    async def sendIllust(self,
                         illust: Illust,
                         message: Optional[Message] = None,
                         chat_id: Optional[int] = None):
        reply_to = message.message_id if message else None
        if not chat_id:
            chat_id = message.chat.id
        elif chat_id != reply_to:  # Sending to different chat, can't reply
            reply_to = None
        try:
            if isinstance(illust, Ugoira):
                await self.send_animation(chat_id,
                                          InputFile(illust.video.path),
                                          caption=sanitizeCaption(
                                              illust.caption),
                                          reply_to_message_id=reply_to)
            else:
                await self.sendPhotos(illust, chat_id, reply_to)
        except BadRequest as error:
            await handleBadRequest(message, error)

    @retry_after
    async def sendDocument(self, file: File, chat_id, message_id=None):
        await self.send_chat_action(chat_id, ChatActions.UPLOAD_DOCUMENT)
        await self.send_document(chat_id,
                                 InputFile(file.path),
                                 reply_to_message_id=message_id)

    async def sendDocuments(self,
                            illust: Illust,
                            message: Optional[Message] = None,
                            chat_id=None):
        if message:
            message_id = message.message_id
            if not chat_id:
                chat_id = message.chat.id
        else:
            message_id = None  # Sending to channel, no message to reply
        for file in illust.all_files:
            await self.sendDocument(file, chat_id, message_id)

    async def updateCollection(self,
                               urls: List[str],
                               message: Optional[Message] = None):
        result = self.sites.match(urls)
        if not result:
            raise NazurinError('No source matched')
        logger.info('Collection update: site=%s, match=%s', result['site'],
                    result['match'].groups())

        illust = await self.sites.handle_update(result)

        # Send / Forward to gallery & Save to album
        # If there're multiple images, then send a new message instead of
        # forwarding an existing one, since we currently can't forward albums correctly.
        if message and message.is_forward(
        ) and not illust.has_multiple_images():
            save = asyncio.create_task(message.forward(config.GALLERY_ID))
        elif not illust.has_image():
            save = asyncio.create_task(
                self.send_message(config.GALLERY_ID, '\n'.join(urls)))
        else:
            save = asyncio.create_task(
                self.sendIllust(illust, message, config.GALLERY_ID))
        download = asyncio.create_task(illust.download())
        await asyncio.gather(save, download)
        await self.storage.store(illust)
        return True
