import asyncio
import aiohttp
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import (
    get_search_results, 
    get_file_details, 
    is_chat_approved, 
    is_user_banned,
    get_all_file_titles,
    save_movie_request,
    get_manual_filter
)
from info import VDISK_API_KEY, OMDB_API_KEY, REQUEST_CHANNEL
from utils import clean_file_name, get_spelling_suggestion, get_google_search_url

DEFAULT_THUMBNAIL = "https://telegra.ph/file/default_poster.jpg"
DELETE_TIME_SECONDS = 120 

def clean_movie_title(title: str) -> str:
    title = re.sub(r'\(.*?\)|\[.*?\]|\b(720p|1080p|480p|2160p|4k|HDRip|WEB-DL|Cam|BDRip|Hindi|English|Gujarati)\b', '', title, flags=re.IGNORECASE)
    return title.strip()

async def fetch_landscape_poster(session: aiohttp.ClientSession, movie_name: str) -> str:
    clean_name = clean_movie_title(movie_name)
    url = f"http://www.omdbapi.com/?t={clean_name}&apikey={OMDB_API_KEY}"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as resp:
            data = await resp.json()
            if data.get("Response") == "True" and data.get("Poster") != "N/A":
                return data.get("Poster")
    except Exception:
        pass
    return DEFAULT_THUMBNAIL

async def get_vdisk_link(session: aiohttp.ClientSession, url: str) -> str:
    api_endpoint = f"https://vdiskpro.com/api?api={VDISK_API_KEY}&url={url}"
    try:
        async with session.get(api_endpoint, timeout=aiohttp.ClientTimeout(total=3)) as resp:
            data = await resp.json()
            if data.get("status") == "success":
                return data.get("shortlink")
    except Exception as e:
        print(f"VDisk Error: {e}")
    return url

async def auto_delete_messages(user_msg, bot_msg, delay=DELETE_TIME_SECONDS):
    await asyncio.sleep(delay)
    try:
        await bot_msg.delete()
    except Exception:
        pass
    try:
        await user_msg.delete()
    except Exception:
        pass

async def notify_admin_auto_request(client, user, movie_name):
    user_info = f"{user.first_name} (@{user.username})" if user.username else f"{user.first_name} (`{user.id}`)"
    await save_movie_request(user.id, user_info, movie_name)

    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Mark as Uploaded", callback_data=f"req_done_{user.id}")]
    ])

    request_msg = (
        "🤖 **Auto Search Request Notification!**\n\n"
        f"👤 **Searched By:** {user_info}\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"🔍 **Movie Not Found:** `{movie_name}`"
    )

    try:
        await client.send_message(chat_id=REQUEST_CHANNEL, text=request_msg, reply_markup=btn)
    except Exception as e:
        print(f"Auto Request Channel Error: {e}")

async def send_manual_filter_reply(client, message, manual_data):
    text = manual_data.get("text", "")
    file_id = manual_data.get("file_id")
    media_type = manual_data.get("media_type")

    if file_id and media_type:
        if media_type == "document":
            bot_msg = await message.reply_document(document=file_id, caption=text)
        elif media_type == "video":
            bot_msg = await message.reply_video(video=file_id, caption=text)
        elif media_type == "photo":
            bot_msg = await message.reply_photo(photo=file_id, caption=text)
        elif media_type == "audio":
            bot_msg = await message.reply_audio(audio=file_id, caption=text)
        else:
            bot_msg = await message.reply_text(text)
    else:
        bot_msg = await message.reply_text(text)
    
    asyncio.create_task(auto_delete_messages(message, bot_msg))

@Client.on_message(filters.group & filters.text & ~filters.command(["start", "index", "request", "add", "del", "viewfilters"]))
async def group_filter_search(client, message):
    if not await is_chat_approved(message.chat.id):
        return

    if message.from_user and await is_user_banned(message.from_user.id):
        return

    raw_query = message.text.strip()

    manual_data = await get_manual_filter(message.chat.id, raw_query)
    if manual_data:
        return await send_manual_filter_reply(client, message, manual_data)

    results = await get_search_results(raw_query)
    corrected_query = None

    if not results:
        all_titles = await get_all_file_titles()
        suggested = await get_spelling_suggestion(raw_query, all_titles)
        if suggested and suggested.lower() != raw_query.lower():
            corrected_query = suggested
            results = await get_search_results(corrected_query)

    if not results:
        if message.from_user:
            asyncio.create_task(notify_admin_auto_request(client, message.from_user, raw_query))

        google_url = get_google_search_url(raw_query)
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Check Correct Spelling on Google", url=google_url)]
        ])

        no_result_msg = await message.reply_text(
            f"❌ **Movie not available in Database!**\n\n"
            f"📡 **Your request has been automatically sent to the Admin.**\n"
            f"If spelling is wrong, check correct spelling using Google button below:",
            reply_markup=buttons
        )
        asyncio.create_task(auto_delete_messages(message, no_result_msg, delay=30))
        return

    bot_username = client.me.username
    display_query = corrected_query if corrected_query else clean_file_name(raw_query)
    
    caption_text = ""
    if corrected_query:
        caption_text += f"💡 **Did you mean:** `{corrected_query}`?\n\n"
    
    caption_text += f"🎬 **Results for:** `{display_query}`\n\n"
    caption_text += "👇 **Download / Stream Links:**\n\n"

    for file in results:
        file_name = clean_file_name(file.get('file_name', 'Unknown File'))
        file_size = file.get('file_size', 'N/A')
        file_id = file.get('file_id')
        
        pm_deep_link = f"https://t.me/{bot_username}?start=file_{file_id}"
        caption_text += f"🔹 [{file_name} ({file_size})]({pm_deep_link})\n\n"

    caption_text += f"⏱️ *This message will be deleted in {int(DELETE_TIME_SECONDS/60)} minutes!*"

    google_url = get_google_search_url(display_query)
    btn_list = [
        [InlineKeyboardButton("📥 Get Files in PM", url=f"https://t.me/{bot_username}?start=search_{display_query}")],
        [InlineKeyboardButton("🔍 Check Spelling on Google", url=google_url)]
    ]

    reply_msg = await message.reply_text(
        text=caption_text,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(btn_list)
    )

    asyncio.create_task(auto_delete_messages(message, reply_msg))

@Client.on_message(filters.private & filters.text & ~filters.command(["start", "index", "ban", "unban", "stats", "request", "add", "del", "viewfilters"]))
async def pm_filter_search(client, message):
    if await is_user_banned(message.from_user.id):
        return await message.reply_text("🚫 **You are banned from using this bot!**")

    raw_query = message.text.strip()

    manual_data = await get_manual_filter(message.chat.id, raw_query)
    if manual_data:
        return await send_manual_filter_reply(client, message, manual_data)

    results = await get_search_results(raw_query)
    corrected_query = None

    if not results:
        all_titles = await get_all_file_titles()
        suggested = await get_spelling_suggestion(raw_query, all_titles)
        if suggested and suggested.lower() != raw_query.lower():
            corrected_query = suggested
            results = await get_search_results(corrected_query)

    if not results:
        asyncio.create_task(notify_admin_auto_request(client, message.from_user, raw_query))

        google_url = get_google_search_url(raw_query)
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Check Correct Spelling on Google", url=google_url)]
        ])
        
        reply_msg = await message.reply_text(
            f"❌ **Movie not available in Database!**\n\n"
            f"📩 **Your automatic request has been sent to the Admin.**",
            reply_markup=buttons
        )
        asyncio.create_task(auto_delete_messages(message, reply_msg, delay=30))
        return

    buttons = []
    for file in results:
        file_name = clean_file_name(file.get('file_name', 'Unknown'))
        file_size = file.get('file_size', 'N/A')
        file_id = file.get('file_id')
        
        btn_text = f"🎬 {file_name} [{file_size}]"
        buttons.append([InlineKeyboardButton(btn_text, callback_data=f"send_{file_id}")])

    google_url = get_google_search_url(corrected_query or raw_query)
    buttons.append([InlineKeyboardButton("🔍 Check Spelling on Google", url=google_url)])

    heading = f"💡 **Did you mean:** `{corrected_query}`?\n\n" if corrected_query else ""
    
    reply_msg = await message.reply_text(
        f"{heading}🔍 **Search Results:** `{clean_file_name(corrected_query or raw_query)}`\n\n⏱️ *This message will be deleted in {int(DELETE_TIME_SECONDS/60)} minutes.*",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    asyncio.create_task(auto_delete_messages(message, reply_msg))

async def send_poster_and_stream(client, message_or_query, file_id):
    file_details = await get_file_details(file_id)
    if not file_details:
        return

    file_name = clean_file_name(file_details.get("file_name", "Unknown File"))
    file_size = file_details.get("file_size", "N/A")
    poster_url = file_details.get("poster")

    target_link = f"https://t.me/{client.me.username}?start=file_{file_id}"

    async with aiohttp.ClientSession() as session:
        if not poster_url or poster_url == "N/A":
            poster_url = await fetch_landscape_poster(session, file_name)
        
        vdisk_link = await get_vdisk_link(session, target_link)

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍿 Stream / Fast Download (VDisk)", url=vdisk_link)],
        [InlineKeyboardButton("❌ Close", callback_data="close_data")]
    ])

    caption = (
        f"🎬 **Title:** `{file_name}`\n"
        f"💾 **Size:** `{file_size}`\n\n"
        "👇 **Click the button below to Watch / Download:**\n\n"
        f"⏱️ *This file card will be deleted in {int(DELETE_TIME_SECONDS/60)} minutes!*"
    )

    user_msg = message_or_query if hasattr(message_or_query, 'delete') else message_or_query.message

    try:
        reply_msg = await user_msg.reply_photo(photo=poster_url, caption=caption, reply_markup=buttons)
    except Exception:
        reply_msg = await user_msg.reply_text(text=caption, reply_markup=buttons)

    asyncio.create_task(auto_delete_messages(user_msg, reply_msg))

@Client.on_callback_query(filters.regex(r"^send_"))
async def send_file_card(client, query):
    await query.answer("⚡ Generating Link...", show_alert=False)
    file_id = query.data.split("_")[1]
    await send_poster_and_stream(client, query, file_id)

@Client.on_callback_query(filters.regex("close_data"))
async def close_cb(client, query):
    await query.message.delete()
        
