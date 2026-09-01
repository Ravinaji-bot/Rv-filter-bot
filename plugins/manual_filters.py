from pyrogram import Client, filters, enums
from database.ia_filterdb import (
    add_manual_filter,
    get_manual_filter,
    delete_manual_filter,
    get_all_manual_filters
)
from info import ADMIN_ID

async def is_admin_or_owner(client, message):
    if message.from_user.id == ADMIN_ID:
        return True
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        try:
            member = await message.chat.get_member(message.from_user.id)
            return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
        except Exception:
            return False
    return False

@Client.on_message(filters.command("add") & (filters.group | filters.private))
async def add_filter_cmd(client, message):
    if not await is_admin_or_owner(client, message):
        return await message.reply_text("❌ Admin access required to add custom filters.")

    args = message.text.split(None, 2)
    reply = message.reply_to_message

    if len(args) < 2:
        return await message.reply_text(
            "⚠️ **How to add manual filter:**\n\n"
            "1. Reply to any message/media:\n`/add keyword`\n\n"
            "2. Send with custom text:\n`/add keyword Reply Text Here`"
        )

    keyword = args[1].lower().strip()
    text = ""
    file_id = None
    media_type = None

    if reply:
        text = reply.caption.html if reply.caption else (reply.text or "")
        if reply.document:
            file_id = reply.document.file_id
            media_type = "document"
        elif reply.video:
            file_id = reply.video.file_id
            media_type = "video"
        elif reply.audio:
            file_id = reply.audio.file_id
            media_type = "audio"
        elif reply.photo:
            file_id = reply.photo.file_id
            media_type = "photo"
    elif len(args) > 2:
        text = args[2]
    else:
        return await message.reply_text("⚠️ Reply to a message or provide text to save as filter.")

    await add_manual_filter(message.chat.id, keyword, text, file_id, media_type)
    await message.reply_text(f"✅ **Manual Filter Added Successfully!**\n\n🔑 **Trigger Keyword:** `{keyword}`")

@Client.on_message(filters.command("del") & (filters.group | filters.private))
async def delete_filter_cmd(client, message):
    if not await is_admin_or_owner(client, message):
        return await message.reply_text("❌ Admin access required to delete filters.")

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** `/del keyword`")

    keyword = message.command[1].lower().strip()
    deleted = await delete_manual_filter(message.chat.id, keyword)

    if deleted:
        await message.reply_text(f"🗑️ **Manual Filter Deleted:** `{keyword}`")
    else:
        await message.reply_text(f"❌ No manual filter found for keyword: `{keyword}`")

@Client.on_message(filters.command("viewfilters") & (filters.group | filters.private))
async def view_filters_cmd(client, message):
    filters_list = await get_all_manual_filters(message.chat.id)

    if not filters_list:
        return await message.reply_text("ℹ️ No manual filters set in this chat yet.")

    text = "📝 **Active Manual Filters in this Chat:**\n\n"
    for f in filters_list:
        text += f"• `{f['keyword']}`\n"

    await message.reply_text(text)
        
