import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import get_search_results, get_file_details, is_user_banned

@Client.on_message(filters.group & filters.text & ~filters.forwarded)
async def auto_filter(client, message):
    if await is_user_banned(message.from_user.id):
        return

    if message.text.startswith("/"):
        return

    query = message.text.strip()
    if len(query) < 2:
        return

    results = await get_search_results(query)
    if not results:
        return

    btn = []
    for file in results:
        file_name = file["file_name"]
        file_id = file["file_id"]
        btn.append([InlineKeyboardButton(f"🎬 {file_name}", callback_data=f"file_{file_id}")])

    await message.reply_text(
        f"🔎 **Search Results for:** `{query}`",
        reply_markup=InlineKeyboardMarkup(btn)
    )

@Client.on_callback_query(filters.regex(r"^file_"))
async def send_file_callback(client, callback_query):
    file_id = callback_query.data.split("_")[1]
    file_doc = await get_file_details(file_id)

    if file_doc:
        await client.send_cached_media(
            chat_id=callback_query.message.chat.id,
            file_id=file_doc["file_id"],
            caption=f"📁 **File Name:** `{file_doc['file_name']}`"
        )
        await callback_query.answer("Sending File...")
    else:
        await callback_query.answer("❌ File not found in database!", show_alert=True)
      
