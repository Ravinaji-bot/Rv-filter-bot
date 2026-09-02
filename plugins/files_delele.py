import re
import logging
from pyrogram import Client, filters
from info import DELETE_CHANNELS
from database.ia_filterdb import Media, Media2, unpack_new_file_id

logger = logging.getLogger(__name__)

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def deletemultiplemedia(bot, message):
    """Delete files automatically from database when deleted or posted in DELETE_CHANNELS"""

    media = message.document or message.video or message.audio
    if not media:
        return

    file_id, _ = unpack_new_file_id(media.file_id)
    file_name = getattr(media, "file_name", "") or ""
    clean_name = re.sub(r"(_|\-|\.|\+)", " ", str(file_name))

    collections = [Media.collection, Media2.collection]

    # 1. Direct ID based deletion
    for col in collections:
        res = await col.delete_one({"_id": file_id})
        if res.deleted_count:
            logger.info("File successfully deleted from DB (by File ID).")
            return

    # 2. Cleaned File Name + Size + Mime match deletion
    query_clean = {
        "file_name": clean_name,
        "file_size": media.file_size,
        "mime_type": media.mime_type
    }

    for col in collections:
        res = await col.delete_many(query_clean)
        if res.deleted_count:
            logger.info("File successfully deleted from DB (by Cleaned Name).")
            return

    # 3. Original File Name + Size + Mime match deletion
    query_exact = {
        "file_name": file_name,
        "file_size": media.file_size,
        "mime_type": media.mime_type
    }

    for col in collections:
        res = await col.delete_many(query_exact)
        if res.deleted_count:
            logger.info("File successfully deleted from DB (by Exact Name).")
            return

    logger.info("File not found in database.")
          
