from pyrogram import Client, filters
from database.ia_filterdb import add_manual_filter, delete_manual_filter

@Client.on_message(filters.group & filters.command("add"))
async def add_filter_cmd(client, message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply_text("⚠️ **Usage:** `/add <keyword> <reply_text>`")
        return

    keyword = args[1]
    reply_text = args[2]
    await add_manual_filter(message.chat.id, keyword, reply_text)
    await message.reply_text(f"✅ Filter added for `{keyword}`")

@Client.on_message(filters.group & filters.command("del"))
async def delete_filter_cmd(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text("⚠️ **Usage:** `/del <keyword>`")
        return

    keyword = args[1]
    deleted = await delete_manual_filter(message.chat.id, keyword)
    if deleted:
        await message.reply_text(f"🗑️ Filter deleted for `{keyword}`")
    else:
        await message.reply_text(f"❌ No filter found for `{keyword}`")
      
