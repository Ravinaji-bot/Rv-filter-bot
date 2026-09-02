import os
import re
import base64
import logging
import random
import asyncio
import aiohttp
import pytz
from datetime import datetime
from .pmfilter import auto_filter 
from Script import script
from database.refer import referdb
from database.config_db import mdb
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram import Client, filters, enums, StopPropagation
from database.ia_filterdb import get_file_details
from database.users_chats_db import db
from info import (
    LOG_CHANNEL, EMOJI_MODE, REACTIONS, UPDATE_CHNL_LNK, PICS, PICS_URL, ADMINS, 
    SUBSCRIPTION, OWNER_LNK, OWNER_UPI_ID, QR_CODE, AUTH_CHANNELS, AUTH_REQ_CHANNELS, 
    FSUB_PICS, CUSTOM_FILE_CAPTION
)
from utils import (
    get_settings, is_subscribed, is_req_subscribed, get_size, 
    temp, clean_filename, get_random_mix_id
)

logger = logging.getLogger(__name__)

TIMEZONE = "Asia/Kolkata"

# Vdiskpro API se short/streaming link banane ka function
async def get_vdisk_link(url_or_file):
    api_key = os.environ.get("VDISK_API_KEY", "YOUR_VDISK_API_KEY")
    api_url = f"https://vdiskpro.com/api?api={api_key}&url={url_or_file}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                res = await response.json()
                if res.get("status") == "success" or "shortlink" in res:
                    return res.get("shortlink") or res.get("url")
                return res.get("url", url_or_file)
    except Exception as e:
        logger.error(f"Vdiskpro API Error: {e}")
        return url_or_file


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        if EMOJI_MODE:
            try:
                await message.react(emoji=random.choice(REACTIONS), big=True)
            except Exception:
                await message.react(emoji="⚡️")

        # Group Start Logic
        if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            buttons = [
                [InlineKeyboardButton('❤️ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ❤️', url=f'http://t.me/{temp.U_NAME}?startgroup=true')],
                [InlineKeyboardButton('🍁 Update Channel 🍁', url=UPDATE_CHNL_LNK)]
            ]
            await message.reply(
                script.GSTART_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), 
                reply_markup=InlineKeyboardMarkup(buttons), 
                disable_web_page_preview=True
            )
            if not await db.get_chat(message.chat.id):
                total = await client.get_chat_members_count(message.chat.id)
                await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
                await db.add_chat(message.chat.id, message.chat.title)
            return 

        # New User Registration
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))

        # Plain /start Command
        if len(message.command) != 2:
            buttons = [
                [InlineKeyboardButton('🔰 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ 🔰', url=f'http://t.me/{temp.U_NAME}?startgroup=true')],
                [InlineKeyboardButton(' ʜᴇʟᴘ 📢', callback_data='help'), InlineKeyboardButton(' ᴀʙᴏᴜᴛ 📖', callback_data='about')],
                [InlineKeyboardButton('ᴛᴏᴘ sᴇᴀʀᴄʜɪɴɢ ⭐', callback_data="topsearch"), InlineKeyboardButton('ᴜᴘɢʀᴀᴅᴇ 🎟', callback_data="premium_info")]
            ]
            curr_time = datetime.now(pytz.timezone(TIMEZONE)).hour        
            gtxt = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 🌞" if curr_time < 12 else ("ɢᴏᴏᴅ ᴀғᴛᴇʀɴᴏᴏɴ 🌓" if curr_time < 17 else ("ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 🌘" if curr_time < 21 else "ɢᴏᴏᴅ ɴɪɢʜᴛ 🌑"))
            
            PIC = PICS[0] if len(PICS) == 1 else f"{random.choice(PICS_URL)}?r={get_random_mix_id()}"
            await message.reply_photo(
                photo=PIC,
                caption=script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
            return

        # Premium Information
        if message.command[1] == "premium":
            buttons = [
                [InlineKeyboardButton('📲 ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ', url=OWNER_LNK)],
                [InlineKeyboardButton('UPI ID Copy Karein', copy_text=OWNER_UPI_ID)],
                [InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')]
            ]
            await message.reply_photo(
                photo=SUBSCRIPTION,
                caption=script.PREPLANS_TXT.format(message.from_user.mention, OWNER_UPI_ID, QR_CODE),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
            return  

        # Inline search redirect
        if message.command[1].startswith('getfile'):
            movies = message.command[1].split("-", 1)[1] 
            message.text = movies.replace('-', ' ') 
            await auto_filter(client, message)
            raise StopPropagation

        data = message.command[1]
        try:
            _, grp_id, file_id = data.split("_", 2)
            grp_id = int(grp_id)
        except Exception:
            grp_id = 0
            file_id = data

        # Force Subscription Check
        btn = []
        settings = await get_settings(grp_id)
        fsub_channels = list(dict.fromkeys((settings.get('fsub', []) if settings else []) + AUTH_CHANNELS)) 

        if fsub_channels:
            btn += await is_subscribed(client, message.from_user.id, fsub_channels)
        if AUTH_REQ_CHANNELS:
            btn += await is_req_subscribed(client, message.from_user.id, AUTH_REQ_CHANNELS)
            
        if btn:
            if "_" in message.command[1]:
                kk, fid = message.command[1].split("_", 1)
                btn.append([InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", callback_data=f"checksub#{kk}#{fid}")])
            photo = random.choice(FSUB_PICS) if FSUB_PICS else "https://graph.org/file/7478ff3eac37f4329c3d8.jpg"
            await message.reply_photo(
                photo=photo,
                caption=script.FORCESUB_TXT.format(message.from_user.mention),
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.HTML
            )
            return

        # Base64 file ID decode
        decoded_file_id = file_id
        if not data.startswith("allfiles"):
            try:
                raw = base64.urlsafe_b64decode(file_id + "=" * (-len(file_id) % 4))
                sep = raw.find(b"_")
                if sep != -1:
                    decoded_file_id = raw[sep + 1:].decode("latin1")
            except Exception:
                pass

        # Message Process indicator
        msg_wait = await message.reply_text("<b>⚡️ Generating Vdiskpro Stream Link...</b>")

        # Send Single File Streaming Link via Vdiskpro
        files_ = await get_file_details(decoded_file_id)
        if files_:
            file_single = files_[0]
            title = clean_filename(file_single.file_name)
            size = get_size(file_single.file_size)

            # Vdiskpro API Link Generation
            # original telegram streaming endpoint ya direct link pass karein
            stream_url = f"https://t.me/{temp.U_NAME}?start=stream_{decoded_file_id}"
            vdisk_link = await get_vdisk_link(stream_url)

            btn = [
                [InlineKeyboardButton("🎬 Watch / Download Stream Link 🎬", url=vdisk_link)],
                [InlineKeyboardButton("🍁 Main Channel 🍁", url=UPDATE_CHNL_LNK)]
            ]

            caption_text = (
                f"<b>📁 File Name:</b> <code>{title}</code>\n"
                f"<b>⚡️ File Size:</b> <code>{size}</code>\n\n"
                f"<i>Neeche diye gaye button par click karke video streaming/download karein:</i>"
            )

            await msg_wait.delete()
            await message.reply_text(
                text=caption_text,
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await msg_wait.edit_text("<b><i>ɴᴏ ꜱᴜᴄʜ ꜰɪʟᴇ ᴇxɪꜱᴛꜱ !</i></b>")

    except Exception as e:
        logger.exception(f"Error in start command: {e}")
                    
