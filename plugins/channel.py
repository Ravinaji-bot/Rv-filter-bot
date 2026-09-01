from pyrogram import Client, filters
from database.ia_filterdb import save_file_to_db

@Client.on_message(filters.channel & (filters.document | filters.video))
async def auto_index_channel_files(client, message):
    try:
        media = message.document or message.video
        if not media:
            return

        file_id = media.file_id
        raw_name = media.file_name or message.caption or "Unknown File"
        file_size = media.file_size

        saved = await save_file_to_db(file_id, raw_name, file_size)
        if saved:
            print(f"✅ Auto Indexed: {raw_name}")
    except Exception as e:
        print(f"Auto Index Error: {e}")
        
