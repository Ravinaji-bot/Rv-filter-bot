import os
import re
import io
import logging
from functools import partial
from datetime import datetime
from typing import Union, BinaryIO, List, Optional, Callable

from pyrogram import StopTransmission, enums, raw, types, utils
from pyrogram.errors import FilePartMissing
from pyrogram.file_id import FileType

from pyrogram import Client

pyro_log = logging.getLogger("pyrogram")
pyro_log.setLevel(logging.WARNING)

log = logging.getLogger(__name__)

async def _resolve_video_cover(client: "Client", peer, cover: Union[str, BinaryIO, None]):
    if cover is None:
        return None

    try:
        if isinstance(cover, str):
            if os.path.isfile(cover):
                uploaded = await client.invoke(
                    raw.functions.messages.UploadMedia(
                        peer=peer,
                        media=raw.types.InputMediaUploadedPhoto(
                            file=await client.save_file(cover)
                        )
                    )
                )
            elif re.match("^https?://", cover):
                uploaded = await client.invoke(
                    raw.functions.messages.UploadMedia(
                        peer=peer,
                        media=raw.types.InputMediaPhotoExternal(url=cover)
                    )
                )
            else:
                return utils.get_input_media_from_file_id(cover, FileType.PHOTO).id
        else:
            uploaded = await client.invoke(
                raw.functions.messages.UploadMedia(
                    peer=peer,
                    media=raw.types.InputMediaUploadedPhoto(
                        file=await client.save_file(cover)
                    )
                )
            )

        return raw.types.InputPhoto(
            id=uploaded.photo.id,
            access_hash=uploaded.photo.access_hash,
            file_reference=uploaded.photo.file_reference
        )
    except Exception:
        log.exception("Failed to prepare video cover")
        return None

async def custom_send_cached_media(
        self: "Client",
        chat_id: Union[int, str],
        file_id: str,
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: List["types.MessageEntity"] = None,
        has_spoiler: bool = None,
        disable_notification: bool = None,
        message_thread_id: int = None,
        reply_to_message_id: int = None,
        reply_to_story_id: int = None,
        reply_to_chat_id: Union[int, str] = None,
        reply_to_monoforum_id: Union[int, str] = None,
        quote_text: str = None,
        quote_entities: List["types.MessageEntity"] = None,
        cover: Union[str, BinaryIO] = None,
        schedule_date: datetime = None,
        protect_content: bool = None,
        allow_paid_broadcast: bool = None,
        invert_media: bool = False,
        reply_markup: Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ] = None
    ) -> Optional["types.Message"]:
        
        peer = await self.resolve_peer(chat_id)
        
        reply_to = None
        if reply_to_message_id or reply_to_story_id:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id,
                story_id=reply_to_story_id,
                chat_id=reply_to_chat_id,
                quote=quote_text,
                quote_parse_mode=parse_mode,
                quote_entities=quote_entities
            )
            reply_to = await utils.get_reply_to(
                client=self,
                reply_parameters=reply_parameters,
                message_thread_id=message_thread_id,
                direct_messages_topic_id=reply_to_monoforum_id
            )
        
        vidcover_file = await _resolve_video_cover(self, peer, cover)
        media = utils.get_input_media_from_file_id(
            file_id,
            has_spoiler=has_spoiler,
            video_cover=vidcover_file
        )

        r = await self.invoke(
            raw.functions.messages.SendMedia(
                peer=await self.resolve_peer(chat_id),
                media=media,
                silent=disable_notification or None,
                reply_to=reply_to,
                random_id=self.rnd_id(),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                noforwards=protect_content,
                allow_paid_floodskip=allow_paid_broadcast,
                invert_media=invert_media,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                **await utils.parse_text_entities(self, caption, parse_mode, caption_entities)
            )
        )

        messages = await utils.parse_messages(client=self, messages=r)
        return messages[0] if messages else None

async def custom_send_video(
        self: "Client",
        chat_id: Union[int, str],
        video: Union[str, BinaryIO],
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: List["types.MessageEntity"] = None,
        has_spoiler: bool = None,
        ttl_seconds: int = None,
        duration: int = 0,
        width: int = 0,
        height: int = 0,
        thumb: Union[str, BinaryIO] = None,
        file_name: str = None,
        supports_streaming: bool = True,
        disable_notification: bool = None,
        message_thread_id: int = None,
        business_connection_id: str = None,
        reply_to_message_id: int = None,
        reply_to_story_id: int = None,
        reply_to_chat_id: Union[int, str] = None,
        reply_to_monoforum_id: Union[int, str] = None,
        quote_text: str = None,
        quote_entities: List["types.MessageEntity"] = None,
        cover: Union[str, BinaryIO] = None,
        start_timestamp: int = None,
        schedule_date: datetime = None,
        protect_content: bool = None,
        allow_paid_broadcast: bool = None,
        message_effect_id: int = None,
        view_once: bool = None,
        invert_media: bool = None,
        reply_markup: Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ] = None,
        progress: Callable = None,
        progress_args: tuple = ()
    ) -> Optional["types.Message"]:
    
        file = None
        peer = await self.resolve_peer(chat_id)

        reply_to = None
        if reply_to_message_id or reply_to_story_id:
            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id,
                story_id=reply_to_story_id,
                chat_id=reply_to_chat_id,
                quote=quote_text,
                quote_parse_mode=parse_mode,
                quote_entities=quote_entities
            )
            reply_to = await utils.get_reply_to(
                client=self,
                reply_parameters=reply_parameters,
                message_thread_id=message_thread_id,
                direct_messages_topic_id=reply_to_monoforum_id
            )
        try:
            vidcover_file = await _resolve_video_cover(self, peer, cover)
            
            if isinstance(video, str):
                if os.path.isfile(video):
                    thumb = await self.save_file(thumb)
                    file = await self.save_file(video, progress=progress, progress_args=progress_args)
                    media = raw.types.InputMediaUploadedDocument(
                        mime_type=self.guess_mime_type(video) or "video/mp4",
                        file=file,
                        ttl_seconds=(1 << 31) - 1 if view_once else ttl_seconds,
                        spoiler=has_spoiler,
                        thumb=thumb,
                        attributes=[
                            raw.types.DocumentAttributeVideo(
                                supports_streaming=supports_streaming or None,
                                duration=duration,
                                w=width,
                                h=height
                            ),
                            raw.types.DocumentAttributeFilename(file_name=file_name or os.path.basename(video))
                        ],
                        video_cover=vidcover_file,
                        video_timestamp=start_timestamp
                    )
                elif re.match("^https?://", video):
                    media = raw.types.InputMediaDocumentExternal(
                        url=video,
                        ttl_seconds=(1 << 31) - 1 if view_once else ttl_seconds,
                        spoiler=has_spoiler,
                        video_cover=vidcover_file,
                        video_timestamp=start_timestamp
                    )
                else:
                    media = utils.get_input_media_from_file_id(
                        video,
                        FileType.VIDEO,
                        ttl_seconds=(1 << 31) - 1 if view_once else ttl_seconds,
                        has_spoiler=has_spoiler,
                        video_cover=vidcover_file,
                        video_start_timestamp=start_timestamp
                    )
            else:
                thumb = await self.save_file(thumb)
                file = await self.save_file(video, progress=progress, progress_args=progress_args)
                media = raw.types.InputMediaUploadedDocument(
                    mime_type=self.guess_mime_type(file_name or video.name) or "video/mp4",
                    file=file,
                    ttl_seconds=(1 << 31) - 1 if view_once else ttl_seconds,
                    spoiler=has_spoiler,
                    thumb=thumb,
                    attributes=[
                        raw.types.DocumentAttributeVideo(
                            supports_streaming=supports_streaming or None,
                            duration=duration,
                            w=width,
                            h=height
                        ),
                        raw.types.DocumentAttributeFilename(file_name=file_name or video.name)
                    ],
                    video_cover=vidcover_file,
                    video_timestamp=start_timestamp
                )

            while True:
                try:
                    rpc = raw.functions.messages.SendMedia(
                        peer=peer,
                        media=media,
                        silent=disable_notification or None,
                        reply_to=reply_to,
                        random_id=self.rnd_id(),
                        schedule_date=utils.datetime_to_timestamp(schedule_date),
                        noforwards=protect_content,
                        allow_paid_floodskip=allow_paid_broadcast,
                        effect=message_effect_id,
                        invert_media=invert_media,
                        reply_markup=await reply_markup.write(self) if reply_markup else None,
                        **await utils.parse_text_entities(self, caption, parse_mode, caption_entities)
                    )
                    if business_connection_id is not None:
                        r = await self.invoke(
                            raw.functions.InvokeWithBusinessConnection(
                                connection_id=business_connection_id,
                                query=rpc
                            )
                        )
                    else:
                        r = await self.invoke(rpc)
                except FilePartMissing as e:
                    await self.save_file(video, file_id=file.id, file_part=e.value)
                else:
                    for i in r.updates:
                        if isinstance(i, (raw.types.UpdateNewMessage,
                                          raw.types.UpdateNewChannelMessage,
                                          raw.types.UpdateNewScheduledMessage,
                                          raw.types.UpdateBotNewBusinessMessage)):
                            return await types.Message._parse(
                                self, i.message,
                                {i.id: i for i in r.users},
                                {i.id: i for i in r.chats},
                                is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage),
                                business_connection_id=business_connection_id
                            )
        except StopTransmission:
            return None


async def custom_copy(
    self: "types.Message",
    chat_id: Union[int, str],
    caption: str = None,
    parse_mode: Optional["enums.ParseMode"] = None,
    caption_entities: list["types.MessageEntity"] = None,
    has_spoiler: bool = None,
    video_cover: Optional[Union[str, "io.BytesIO"]] = None,
    disable_notification: bool = None,
    message_thread_id: int = None,
    quote_text: str = None,
    quote_entities: List["types.MessageEntity"] = None,
    reply_to_message_id: int = None,
    reply_to_chat_id: int = None,
    schedule_date: datetime = None,
    protect_content: bool = None,
    allow_paid_broadcast: bool = None,
    invert_media: bool = None,
    reply_markup: Union[
        "types.InlineKeyboardMarkup",
        "types.ReplyKeyboardMarkup",
        "types.ReplyKeyboardRemove",
        "types.ForceReply"
    ] = object
) -> Union["types.Message", List["types.Message"]]:

    if self.service:
        log.warning("Service messages cannot be copied. chat_id: %s, message_id: %s",
                    self.chat.id, self.id)
    elif self.game and not await self._client.storage.is_bot():
        log.warning("Users cannot send messages with Game media type. chat_id: %s, message_id: %s",
                    self.chat.id, self.id)
    elif self.empty:
        log.warning("Empty messages cannot be copied.")
    elif self.text:
        return await self._client.send_message(
            chat_id,
            text=self.text,
            entities=self.entities,
            parse_mode=enums.ParseMode.DISABLED,
            disable_web_page_preview=not self.web_page_preview,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            reply_to_message_id=reply_to_message_id,
            reply_to_chat_id=reply_to_chat_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
            schedule_date=schedule_date,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            reply_markup=self.reply_markup if reply_markup is object else reply_markup
        )
    elif self.media:
        send_media = partial(
            self._client.send_cached_media,
            chat_id=chat_id,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            reply_to_message_id=reply_to_message_id,
            reply_to_chat_id=reply_to_chat_id,
            schedule_date=schedule_date,
            has_spoiler=has_spoiler,
            protect_content=protect_content,
            allow_paid_broadcast=allow_paid_broadcast,
            invert_media=invert_media,
            reply_markup=self.reply_markup if reply_markup is object else reply_markup,
            cover=video_cover
        )

        if self.photo:
            file_id = self.photo.file_id
            return await send_media(file_id=file_id)
        elif self.audio:
            file_id = self.audio.file_id
            return await send_media(file_id=file_id)
        elif self.document:
            file_id = self.document.file_id
            return await send_media(file_id=file_id)
        elif self.video:
            return await self._client.send_video(
                chat_id,
                video=self.video.file_id,
                caption=caption,
                parse_mode=parse_mode,
                caption_entities=caption_entities,
                invert_media=invert_media or self.invert_media,
                cover=video_cover,
                has_spoiler=self.has_media_spoiler,
                disable_location=None,
                disable_notification=disable_notification,
                protect_content=self.has_protected_content if protect_content is None else protect_content,
                allow_paid_broadcast=allow_paid_broadcast,
                message_thread_id=self.message_thread_id if message_thread_id is None else message_thread_id,
                reply_markup=self.reply_markup if reply_markup is object else reply_markup,
                schedule_date=schedule_ye := schedule_date,
                reply_to_message_id=reply_to_message_id
            )
        elif self.animation:
            file_id = self.animation.file_id
            return await send_media(file_id=file_id)
        elif self.voice:
            file_id = self.voice.file_id
            return await send_media(file_id=file_id)
        elif self.sticker:
            file_id = self.sticker.file_id
            return await send_media(file_id=file_id)
        elif self.video_note:
            file_id = self.video_note.file_id
            return await send_media(file_id=file_id)
        elif self.current_media := getattr(self, "contact", None):
            return await self._client.send_contact(
                chat_id,
                phone_number=self.contact.phone_number,
                first_name=self.contact.first_name,
                last_name=self.contact.last_name,
                vcard=self.contact.vcard,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                schedule_date=schedule_date,
                allow_paid_broadcast=allow_paid_broadcast,
            )
        elif getattr(self, "location", None):
            return await self._client.send_location(
                chat_id,
                latitude=self.location.latitude,
                longitude=self.location.longitude,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                schedule_date=schedule_date,
                allow_paid_broadcast=allow_paid_broadcast
            )
        elif getattr(self, "venue", None):
            return await self._client.send_venue(
                chat_id,
                latitude=self.venue.location.latitude,
                longitude=self.venue.location.longitude,
                title=self.venue.title,
                address=self.venue.address,
                foursquare_id=self.venue.foursquare_id,
                foursquare_type=self.venue.foursquare_type,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                schedule_date=schedule_date,
                allow_paid_broadcast=allow_paid_broadcast
            )
        elif getattr(self, "poll", None):
            return await self._client.send_poll(
                chat_id,
                question=self.poll.question,
                options=[
                    types.InputPollOption(
                        text=opt.text
                    ) for opt in self.poll.options
                ],
                disable_notification=disable_keyword := disable_notification,
                message_thread_id=message_thread_id,
                schedule_date=schedule_date,
                allow_paid_broadcast=allow_paid_broadcast
            )
        elif getattr(self, "game", None):
            return await self._client.send_game(
                chat_id,
                game_short_name=self.game.short_name,
                disable_notification=disable_notification,
                message_thread_id=message_thread_id,
                allow_paid_broadcast=allow_paid_broadcast
            )

Client.send_cached_media = custom_send_cached_media
Client.se
