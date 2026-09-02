import logging
from utils import (
    get_size, is_check_admin, get_poster, get_posterx, temp, 
    get_settings, save_group_settings, get_cap, clean_filename, 
    clean_search_text, get_settings_text
)
from rapidfuzz import process
from urllib.parse import quote_plus

from database.ia_filterdb import Media, Media2, get_search_results, get_bad_files
from database.config_db import mdb
from pyrogram.errors import MessageIdInvalid, UserIsBlocked, MessageNotModified, PeerIdInvalid, MessageDeleteForbidden
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from info import (
    ADMINS, DELETE_TIME, EMOJI_MODE, GRP_LNK, LANDSCAPE_POSTER, 
    LANGUAGES, LOG_CHANNEL, MAX_B_TN, MSG_ALRT, MULTIPLE_DB, NO_RESULTS_MSG, 
    OWNER_LNK, PICS, QUALITIES, REACTIONS, REQST_CHANNEL, SEASONS, 
    SUPPORT_CHAT_ID, TMDB_ON_SEARCH, TMDB_POSTER, ULTRA_FAST_MODE, URL,
    VDISK_DOMAIN, VDISK_API
)
from Script import script
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from database.users_chats_db import db
import asyncio
import re
import math
import random
import pytz
from datetime import datetime, timedelta
lock = asyncio.Lock()

logger = logging.getLogger(__name__)

TIMEZONE = "Asia/Kolkata"
BUTTON = {}
BUTTONS = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}
SPELL_CHECK = {}

@Client.on_message(filters.group & filters.text & filters.incoming & ~filters.regex(r"^/"))
async def give_filter(client, message):
    if EMOJI_MODE:
        try:
            await message.react(emoji=random.choice(REACTIONS), big=True)
        except Exception:
            await message.react(emoji="⚡️")
            pass
    await mdb.update_top_messages(message.from_user.id, message.text)
    if message.chat.id != SUPPORT_CHAT_ID:
        settings = await get_settings(message.chat.id)
        try:
            if settings['auto_ffilter']:
                if re.search(r'https?://\S+|www\.\S+|t\.me/\S+', message.text):
                    if await is_check_admin(client, message.chat.id, message.from_user.id):
                        return
                    return await message.delete()
                await auto_filter(client, message)
        except KeyError:
            await save_group_settings(message.chat.id, 'auto_ffilter', True)
            settings = await get_settings(message.chat.id)
            if settings['auto_ffilter']:
                await auto_filter(client, message) 
        except Exception as e:
            logger.exception("Error in auto filter: %s", e)
            pass
    else:
        search = message.text
        _, _, total_results = await get_search_results(chat_id=message.chat.id, query=search.lower(), offset=0, filter=True)
        if total_results == 0:
            return
        await message.reply_text(
            script.ALREADY_AVAILABLE_TXT.format(message.from_user.mention, total_results, search),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔍 ᴊᴏɪɴ ᴀɴᴅ ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ 🔎", url=GRP_LNK)]])
        )

@Client.on_message(filters.private & filters.text & filters.incoming & ~filters.regex(r"^/") & ~filters.regex(r"(https?://)?(t\.me|telegram\.me|telegram\.dog)/"))
async def pm_text(bot, message):
    bot_id = bot.me.id
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if EMOJI_MODE:
        try:
            await message.react(emoji=random.choice(REACTIONS), big=True)
        except Exception:
            await message.react(emoji="⚡️")
            pass
    if content.startswith(("#")):
        return
    try:
        await mdb.update_top_messages(user_id, content)
        pm_search = await db.pm_search_status(bot_id)
        if pm_search:
            await auto_filter(bot, message)
        else:
            await message.reply_text(
                text=script.PM_SEARCH_DISABLED_TXT.format(user),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ ", url=GRP_LNK)]])
            )
            await bot.send_message(
                chat_id=LOG_CHANNEL,
                text=script.PM_LOG_TXT.format(user, user_id, content)
            )
    except Exception:
        pass

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    try:
        await query.answer()
    except Exception:
        pass
    ident, req, key, offset = query.data.split("_")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except Exception:
        offset = 0
    if BUTTONS.get(key) is not None:
        search = BUTTONS.get(key)
    else:
        search = FRESH.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        return
    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except Exception:
        n_offset = 0

    if not files:
        return
    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    
    # Direct Vdiskpro Stream & File Buttons Structure
    btn = []
    for file in files:
        # Generate Direct Vdisk Streaming URL
        stream_url = f"{VDISK_DOMAIN}/watch/{file.file_id}" if VDISK_DOMAIN else f"{URL}watch/{file.file_id}"
        btn.append([
            InlineKeyboardButton(text=f"📁 {get_size(file.file_size)} - {clean_filename(file.file_name)}", callback_data=f'file#{file.file_id}'),
            InlineKeyboardButton(text="🎬 Stream/Download", url=stream_url)
        ])

    btn.insert(0, [
        InlineKeyboardButton('Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{req}#{key}"),
        InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{req}#{key}"),
        InlineKeyboardButton("Sᴇᴀsᴏɴ", callback_data=f"seasons#{req}#{key}")
    ])

    if ULTRA_FAST_MODE:
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append([InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1}", callback_data="pages")])
        elif off_set is None:
            btn.append([InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
        else:
            btn.append([
                InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1}", callback_data="pages"),
                InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
            ])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except (MessageNotModified, MessageIdInvalid):
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, id, user = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    movies = await get_posterx(id, id=True) if TMDB_ON_SEARCH else await get_poster(id, id=True)
    movie = movies.get('title')
    movie = re.sub(r"[:-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        await auto_filter(bot, query, k)
    else:
        reqstr1 = query.from_user.id if query.from_user else 0
        reqstr = await bot.get_users(reqstr1)
        if NO_RESULTS_MSG:
            try:
                await bot.send_message(chat_id=LOG_CHANNEL, text=script.NORSLTS.format(reqstr.id, reqstr.mention, movie))
            except Exception as e:
                logger.error("Error In Spol: %s", e)
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔰 ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴀᴅᴍɪɴ 🔰", url=OWNER_LNK)]])
        k = await query.message.edit(script.MVE_NT_FND, reply_markup=btn)
        await asyncio.sleep(10)
        await k.delete()
        # Qualities Filter Callback
@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):
    _, req, key = query.data.split("#")
    try:
        if int(req) not in [query.from_user.id, 0]:
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    except Exception:
        pass

    btn = []
    for i in range(0, len(QUALITIES), 2):
        q1 = QUALITIES[i]
        row = [InlineKeyboardButton(text=q1, callback_data=f"fq#{q1.lower()}#{req}#{key}")]
        if i + 1 < len(QUALITIES):
            q2 = QUALITIES[i + 1]
            row.append(InlineKeyboardButton(text=q2, callback_data=f"fq#{q2.lower()}#{req}#{key}"))
        btn.append(row)

    btn.insert(0, [InlineKeyboardButton(text="⇊ ꜱᴇʟᴇᴄᴛ ǫᴜᴀʟɪᴛʏ ⇊", callback_data="ident")])
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ↭", callback_data=f"fq#homepage#{req}#{key}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^fq#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    _, qual, req, key = query.data.split("#")
    search = FRESH.get(key, "")
    
    # Dash aur hyphens ko remove karke clean string banayein
    search = re.sub(r"[-_–—]", " ", search)
    search = re.sub(r"\s+", " ", search).strip()
    
    chat_id = query.message.chat.id
    try:
        if int(req) not in [query.from_user.id, 0]:
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    except Exception:
        pass

    if qual != "homepage":
        search = f"{search} {qual}"

    BUTTONS[key] = search
    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    
    if not files:
        return await query.answer("🚫 ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫", show_alert=True)

    btn = []
    for file in files:
        stream_url = f"{VDISK_DOMAIN}/watch/{file.file_id}" if VDISK_DOMAIN else f"{URL}watch/{file.file_id}"
        btn.append([
            InlineKeyboardButton(text=f"📁 {get_size(file.file_size)} - {clean_filename(file.file_name)}", callback_data=f'file#{file.file_id}'),
            InlineKeyboardButton(text="🎬 Stream", url=stream_url)
        ])

    btn.insert(0, [
        InlineKeyboardButton('Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{req}#{key}"),
        InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{req}#{key}"),
        InlineKeyboardButton("Sᴇᴀsᴏɴ", callback_data=f"seasons#{req}#{key}")
    ])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except Exception:
        pass
    await query.answer()


# Auto Filter Core Handler
async def auto_filter(client, msg, spoll=None):
    if spoll:
        message = msg.message
        search, files, offset, total_results = spoll
    else:
        message = msg
        search = message.text

    # Strict search text cleaning (Desk / Dash remove karne ke liye)
    search = re.sub(r"[-_–—]", " ", search)
    search = re.sub(r"\s+", " ", search).strip()

    if not spoll:
        files, offset, total_results = await get_search_results(message.chat.id, search, offset=0, filter=True)

    if not files:
        if SPELL_CHECK_REPLY:
            return await advantage_spoll_choker(client, message)
        return

    key = f"{message.chat.id}-{message.id}"
    FRESH[key] = search

    btn = []
    for file in files:
        stream_url = f"{VDISK_DOMAIN}/watch/{file.file_id}" if VDISK_DOMAIN else f"{URL}watch/{file.file_id}"
        btn.append([
            InlineKeyboardButton(text=f"📁 {get_size(file.file_size)} - {clean_filename(file.file_name)}", callback_data=f'file#{file.file_id}'),
            InlineKeyboardButton(text="🎬 Stream", url=stream_url)
        ])

    btn.insert(0, [
        InlineKeyboardButton('Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{message.from_user.id}#{key}"),
        InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{message.from_user.id}#{key}"),
        InlineKeyboardButton("Sᴇᴀsᴏɴ", callback_data=f"seasons#{message.from_user.id}#{key}")
    ])

    cap = script.CAPTION.format(
        file_name=clean_filename(files[0].file_name),
        file_size=get_size(files[0].file_size),
        file_url=f"{VDISK_DOMAIN}/watch/{files[0].file_id}"
    )

    try:
        await message.reply_text(
            text=cap,
            reply_markup=InlineKeyboardMarkup(btn),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.exception("Error sending auto filter message: %s", e)
        
