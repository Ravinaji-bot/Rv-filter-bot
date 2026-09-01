import logging
from pyrogram import Client, filters
from database.ia_filterdb import save_file_to_db

@Client.on_message(filters.channel & (filters.document | filters.video | filters.audio))
async def auto_index_channel_files(client, message):
    media = message.document or message.video or message.audio
    if not media:
        return

    file_id = media.file_id
    file_name = getattr(media, "file_name", "Unknown File")
    file_size = getattr(media, "file_size", 0)

    saved = await save_file_to_db(file_id, file_name, file_size)
    if saved:
        logging.info(f"Auto-Indexed: {file_name}")
      
