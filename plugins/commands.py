import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS, LOG_CHANNEL
from database.ia_filterdb import get_db_stats, add_user_to_db

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    await add_user_to_db(message.from_user.id, message.from_user.first_name)
    buttons = [
        [InlineKeyboardButton("📢 Channel", url="https://t.me/Telegram"),
         InlineKeyboardButton("💬 Support Group", url="https://t.me/Telegram")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        f"👋 **Namaste {message.from_user.first_name}!**\n\n"
        f"Main Auto-Filter Bot hoon. Group me movie ya file ka naam bhejein, main aapko exact match de dunga!",
        reply_markup=reply_markup
    )

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_command(client, message):
    msg = await message.reply_text("Fetching Database Stats...")
    stats = await get_db_stats()
    text = (
        f"📊 **Database Statistics:**\n\n"
        f"📁 **Total Files:** `{stats['total_files']}`\n"
        f"👥 **Total Users:** `{stats['total_users']}`\n"
        f"👥 **Approved Chats:** `{stats['total_chats']}`\n"
        f"📌 **Manual Filters:** `{stats['total_manual_filters']}`\n"
        f"💾 **Database Size:** `{stats['db_size']}`"
    )
    await msg.edit_text(text)
  
