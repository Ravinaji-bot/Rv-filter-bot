import asyncio
import os
import logging
import aiofiles
import tempfile
import uuid
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegraph import Telegraph
from pymediainfo import MediaInfo

from database.ia_filterdb import get_file_details
from info import BIN_CHANNEL
from dreamxbotz.util.file_properties import get_name

logger = logging.getLogger(__name__)

# Telegraph Init with Fallback
TELEGRAPH_ACCESS_TOKEN = os.environ.get("TELEGRAPH_ACCESS_TOKEN") or "38a8ac190ac77ad863fa0c3fa98bdf0bb563fa200211b168062e5313b401"

try:
    telegraph = Telegraph(access_token=TELEGRAPH_ACCESS_TOKEN)
except Exception:
    telegraph = Telegraph()
    try:
        telegraph.create_account(short_name="DreamxBotz")
    except Exception as e:
        logger.error(f"Failed to initialize Telegraph: {e}")


def format_track(lang: str | None, title: str | None) -> str:
    lang = (lang or "").strip()
    title = (title or "").strip()

    if lang and lang.lower() != "und":
        return lang
    if title:
        return title
    return "und"


@Client.on_callback_query(filters.regex(r"^extract_data"), group=2)
async def extract_data_handler(client: Client, query: CallbackQuery):
    try:
        await query.answer("Fetching Track Details...", show_alert=False)
    except Exception:
        pass

    try:
        _, file_id = query.data.split(":")
    except ValueError:
        return await query.message.reply_text("❌ Invalid Callback Data.", quote=True)

    current_markup = query.message.reply_markup
    wait_keyboard = []

    # Update Button to Loading state
    if current_markup and getattr(current_markup, "inline_keyboard", None):
        for row in current_markup.inline_keyboard:
            new_row = []
            for btn in row:
                if btn.callback_data == query.data:
                    new_row.append(
                        InlineKeyboardButton("ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ... ⏳", callback_data="wait_data")
                    )
                else:
                    new_row.append(btn)
            wait_keyboard.append(new_row)

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(wait_keyboard))
    except Exception:
        pass

    temp_path = os.path.join(
        tempfile.gettempdir(),
        f"extract_{query.from_user.id}_{uuid.uuid4().hex}.tmp"
    )

    try:
        files_ = await get_file_details(file_id)
        if not files_:
            await query.message.reply_text("❌ File not found in Database.", quote=True)
            return

        if query.message and query.message.media:
            log_msg = query.message
        else:
            log_msg = await client.send_cached_media(
                chat_id=BIN_CHANNEL,
                file_id=file_id
            )

        file_name = get_name(log_msg)
        safe_title = (
            file_name.replace(".", " ")
            .replace("_", " ")
            .replace("-", " ")
            .replace("[", "")
            .replace("]", "")
            .replace("(", "")
            .replace(")", "")
            .replace("mkv", "")
            .replace("mp4", "")
            .strip()
        )

        media = getattr(log_msg, log_msg.media.value) if log_msg and log_msg.media else None
        file_size = getattr(media, "file_size", 0) or 0
        chunk_limit = 5 if file_size > 200 * 1024 * 1024 else 3

        # Download header chunk for MediaInfo parsing
        async with aiofiles.open(temp_path, "wb") as f:
            async for chunk in client.stream_media(log_msg, limit=chunk_limit):
                await f.write(chunk)

        lib_path = os.path.abspath("MediaInfo.dll") if os.path.exists("MediaInfo.dll") else None

        # Parse MediaInfo in thread
        media_info = await asyncio.wait_for(
            asyncio.to_thread(MediaInfo.parse, temp_path, library_file=lib_path),
            timeout=8
        )

        audio_tracks = []
        subtitle_tracks = []
        video_info = []

        seen_audio = set()
        seen_subs = set()

        for track in media_info.tracks:
            ttype = (track.track_type or "").lower()

            if ttype == "video":
                codec = track.format or track.codec_id or "Unknown"
                width = track.width or "?"
                height = track.height or "?"
                video_info.append(f"Video: {codec} {width}x{height}")

            elif ttype == "audio":
                lang = (
                    track.other_language[0]
                    if getattr(track, "other_language", None)
                    else track.language or "und"
                )
                key = (lang, track.title)
                if key not in seen_audio:
                    seen_audio.add(key)
                    audio_tracks.append({
                        "language": lang,
                        "title": track.title
                    })

            elif ttype in ("text", "subtitle"):
                lang = (
                    track.other_language[0]
                    if getattr(track, "other_language", None)
                    else track.language or "und"
                )
                key = (lang, track.title)
                if key not in seen_subs:
                    seen_subs.add(key)
                    subtitle_tracks.append({
                        "language": lang,
                        "title": track.title
                    })

        # Build HTML Content for Telegraph
        page_parts = ["<h3><b>Available Audio & Subtitle Tracks</b></h3><br>"]

        if video_info:
            page_parts.append("<b>Video Details:</b><br>")
            for v in video_info:
                page_parts.append(f"<blockquote>• {v}</blockquote>")
            page_parts.append("<br>")

        if audio_tracks:
            page_parts.append(f"<b>Audio Tracks ({len(audio_tracks)}):</b><br>")
            for a in audio_tracks:
                page_parts.append(
                    f"<blockquote>• {format_track(a['language'], a['title'])}</blockquote>"
                )
            page_parts.append("<br>")
        else:
            page_parts.append("<b>Audio Tracks:</b> None<br><br>")

        if subtitle_tracks:
            page_parts.append(f"<b>Subtitle Tracks ({len(subtitle_tracks)}):</b><br>")
            for s in subtitle_tracks:
                page_parts.append(
                    f"<blockquote>• {format_track(s['language'], s['title'])}</blockquote>"
                )
            page_parts.append("<br>")
        else:
            page_parts.append("<b>Subtitle Tracks:</b> None<br><br>")

        page_parts.append('<i><code>Extracted via AutoFilter Bot</code></i>')

        page_content = "".join(page_parts)

        # Create Telegraph Page asynchronously
        response = await asyncio.to_thread(
            telegraph.create_page,
            title=safe_title[:200] or "Track Details",
            html_content=page_content,
            author_name="DreamxBotz"
        )

        telegraph_url = response["url"]

        # Replace Loading button with Telegraph View button
        success_keyboard = []
        if current_markup and getattr(current_markup, "inline_keyboard", None):
            for row in current_markup.inline_keyboard:
                new_row = []
                for btn in row:
                    if btn.callback_data == query.data or btn.callback_data == "wait_data":
                        new_row.append(
                            InlineKeyboardButton("📝 ᴠɪᴇᴡ ᴛʀᴀᴄᴋꜱ 📝", url=telegraph_url)
                        )
                    else:
                        new_row.append(btn)
                success_keyboard.append(new_row)

        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(success_keyboard)
        )

    except asyncio.TimeoutError:
        await query.message.reply_text("⏱ MediaInfo extraction timed out.", quote=True)
    except Exception as e:
        logger.exception(f"Extract Handler Error: {e}")
        await query.message.reply_text(f"❌ Error extracting tracks: {e}", quote=True)

    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
      
