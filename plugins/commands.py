import asyncio
import math
import psutil
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import (
    save_file_to_db, 
    get_db_stats, 
    ban_user_in_db, 
    unban_user_in_db,
    save_movie_request,
    add_user_to_db
)
from info import ADMIN_ID, REQUEST_CHANNEL, LOG_CHANNEL

def make_progress_bar(current: int, total: int) -> str:
    percentage = (current / total) * 100
    filled = math.floor((percentage / 100) * 10)
    unfilled = 10 - filled
    bar = "█" * filled + "░" * unfilled
    return f"`[{bar}]` **{percentage:.1f}%**"

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user = message.from_user
    user_name = f"{user.first_name} (@{user.username})" if user.username else user.first_name
    
    is_new = await add_user_to_db(user.id, user_name)
    if is_new:
        try:
            log_text = (
                "👤 **#New_User Joined Bot!**\n\n"
                f"• **Name:** {user.first_name}\n"
                f"• **ID:** `{user.id}`\n"
                f"• **Username:** @{user.username if user.username else 'None'}"
            )
            await client.send_message(chat_id=LOG_CHANNEL, text=log_text)
        except Exception as e:
            print(f"New User Log Error: {e}")

    await message.reply_text(f"👋 **Hello {user.first_name}!**\n\nJust send me any Movie or Series name to search!")

@Client.on_message(filters.command("request") & (filters.private | filters.group))
async def request_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ **How to use:**\n`/request <Movie Name>`\n\n"
            "Example: `/request Inception 2010`"
        )

    movie_name = message.text.split(None, 1)[1].strip()
    user = message.from_user
    user_info = f"{user.first_name} (@{user.username})" if user.username else f"{user.first_name} (`{user.id}`)"

    await save_movie_request(user.id, user_info, movie_name)

    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Mark as Uploaded / Done", callback_data=f"req_done_{user.id}")]
    ])

    request_msg = (
        "📥 **New Anonymous Movie Request!**\n\n"
        f"👤 **Requested By:** {user_info}\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"🎬 **Requested Movie:** `{movie_name}`"
    )

    try:
        await client.send_message(chat_id=REQUEST_CHANNEL, text=request_msg, reply_markup=btn)
    except Exception as e:
        print(f"Failed to send request to Request Channel: {e}")

    await message.reply_text(
        f"✅ **Your request has been successfully registered!**\n\n"
        f"🎬 **Movie:** `{movie_name}`\n"
        "It will be updated in the system as soon as available."
    )

@Client.on_callback_query(filters.regex(r"^req_done_"))
async def request_done_callback(client, query):
    if query.from_user.id != ADMIN_ID:
        return await query.answer("❌ Access Denied! Admin only feature.", show_alert=True)
    
    await query.message.edit_text(
        f"{query.message.text.markdown}\n\n✅ **Status:** `Handled & Completed`"
    )
    await query.answer("Request Status Updated!")

@Client.on_message(filters.command("index") & filters.private)
async def batch_index_command(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply_text("❌ Access Denied! Admin feature only.")

    if not message.reply_to_message or not message.reply_to_message.forward_from_chat:
        return await message.reply_text("⚠️ Please forward a message from channel and reply with `/index`.")

    msg = await message.reply_text("⏳ **Starting Indexing Process...**")
    chat_id = message.reply_to_message.forward_from_chat.id
    last_msg_id = message.reply_to_message.forward_from_message_id
    
    total_messages = last_msg_id
    current_count = 0
    total_saved_files = 0
    duplicate_files = 0

    try:
        async for channel_msg in client.get_chat_history(chat_id, limit=last_msg_id):
            current_count += 1
            media = channel_msg.document or channel_msg.video
            
            if media:
                file_id = media.file_id
                raw_name = media.file_name or channel_msg.caption or "Unknown File"
                file_size = media.file_size

                saved = await save_file_to_db(file_id, raw_name, file_size)
                if saved:
                    total_saved_files += 1
                else:
                    duplicate_files += 1

            if current_count % 20 == 0 or current_count == total_messages:
                progress_ui = make_progress_bar(current_count, total_messages)
                try:
                    await msg.edit_text(
                        f"⚡ **Live Indexing Progress...**\n\n"
                        f"{progress_ui}\n\n"
                        f"📊 **Scanned:** `{current_count}/{total_messages}`\n"
                        f"✅ **Cleaned & Saved:** `{total_saved_files}`\n"
                        f"⚠️ **Duplicates Skipped:** `{duplicate_files}`"
                    )
                except Exception:
                    pass
                await asyncio.sleep(1)

        final_progress = make_progress_bar(total_messages, total_messages)
        await msg.edit_text(
            f"🎉 **Indexing 100% Completed!**\n\n"
            f"{final_progress}\n\n"
            f"✅ **Saved:** `{total_saved_files}` | ⚠️ **Skipped:** `{duplicate_files}`"
        )
    except Exception as e:
        await msg.edit_text(f"❌ **Error:** `{e}`")

@Client.on_message(filters.command("stats") & filters.private)
async def bot_stats_command(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply_text("❌ Access Denied! Admin feature only.")

    msg = await message.reply_text("🔄 **Fetching Stats...**")
    try:
        stats = await get_db_stats()
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_used_mb = ram.used / (1024 * 1024)
        ram_total_mb = ram.total / (1024 * 1024)
        
        stats_text = (
            "📊 **Live Bot & Server Statistics**\n\n"
            "🖥️ **Server Hardware Status:**\n"
            f"🔹 **CPU Usage:** `{cpu_usage}%`\n"
            f"🔹 **RAM Usage:** `{ram.percent}%` (`{ram_used_mb:.1f}MB` / `{ram_total_mb:.1f}MB`)\n\n"
            "📁 **Database Status:**\n"
            f"🔹 **Total Users:** `{stats['total_users']:,}`\n"
            f"🔹 **Total Indexed Files:** `{stats['total_files']:,}`\n"
            f"🔹 **Manual Filters:** `{stats['total_manual_filters']:,}`\n"
            f"🔹 **Approved Groups:** `{stats['total_chats']}`\n"
            f"🔹 **DB Storage Used:** `{stats['db_size']}`\n\n"
            "⚡ **System Status:** `Online & Operational`"
        )
        await msg.edit_text(stats_text)
    except Exception as e:
        await msg.edit_text(f"❌ Stats Error: `{e}`")

@Client.on_message(filters.command("ban") & filters.private)
async def ban_user_command(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply_text("❌ Access Denied! Admin feature only.")
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** `/ban <User_ID>`")
    try:
        user_id = int(message.command[1])
        await ban_user_in_db(user_id)
        await message.reply_text(f"🚫 **User Banned Successfully!**\nID: `{user_id}`")
    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`")

@Client.on_message(filters.command("unban") & filters.private)
async def unban_user_command(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply_text("❌ Access Denied! Admin feature only.")
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** `/unban <User_ID>`")
    try:
        user_id = int(message.command[1])
        await unban_user_in_db(user_id)
        await message.reply_text(f"✅ **User Unbanned Successfully!**\nID: `{user_id}`")
    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`")
                                  
