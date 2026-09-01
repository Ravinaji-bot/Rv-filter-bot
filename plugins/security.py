import asyncio
import re
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import is_chat_approved, approve_chat_in_db, remove_approved_chat
from info import ADMIN_ID, LOG_CHANNEL

URL_PATTERN = re.compile(r'(https?://|www\.|t\.me|telegram\.me|youtube\.com|youtu\.be|instagram\.com|facebook\.com)\S+', re.IGNORECASE)
MENTION_PATTERN = re.compile(r'@\w+', re.IGNORECASE)

@Client.on_message(filters.group & filters.new_chat_members)
async def group_add_security(client, message):
    for member in message.new_chat_members:
        if member.id == client.me.id:
            chat = message.chat
            added_by = message.from_user.mention if message.from_user else "Unknown User"
            
            try:
                group_log_text = (
                    "👥 **#New_Group Added Bot!**\n\n"
                    f"• **Group Name:** `{chat.title}`\n"
                    f"• **Group ID:** `{chat.id}`\n"
                    f"• **Added By:** {added_by}\n"
                )
                await client.send_message(chat_id=LOG_CHANNEL, text=group_log_text)
            except Exception as e:
                print(f"New Group Log Error: {e}")

            if await is_chat_approved(chat.id):
                return

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"app_grp_{chat.id}"),
                    InlineKeyboardButton("❌ Reject & Leave", callback_data=f"rej_grp_{chat.id}")
                ]
            ])
            
            try:
                await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=(
                        f"🚨 **New Group Security Alert!**\n\n"
                        f"🏷️ **Group Name:** `{chat.title}`\n"
                        f"🆔 **Group ID:** `{chat.id}`\n"
                        f"👤 **Added By:** {added_by}\n\n"
                        "Do you want to approve this group?"
                    ),
                    reply_markup=buttons
                )
            except Exception as e:
                print(f"Log Channel Alert Error: {e}")

            await message.reply_text(
                "⚠️ **Security Notice:**\n\n"
                "This group is not approved by the Bot Admin yet!\n"
                "Bot will not function here until Admin approves it."
            )
        
        elif member.is_bot:
            try:
                await client.ban_chat_member(message.chat.id, member.id)
                await message.delete()
                
                warn_msg = await message.reply_text(
                    f"🚫 **Anti-Bot Protection:**\n"
                    f"Adding unauthorized bots ({member.mention}) is strictly prohibited! Bot has been banned."
                )
                await asyncio.sleep(10)
                await warn_msg.delete()
            except Exception as e:
                print(f"Failed to ban bot: {e}")

@Client.on_message(filters.group & (filters.text | filters.caption) & ~filters.service)
async def auto_link_and_mention_eraser(client, message):
    text = message.text or message.caption or ""
    
    try:
        user_member = await message.chat.get_member(message.from_user.id)
        if user_member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            return
    except Exception:
        pass

    if URL_PATTERN.search(text) or MENTION_PATTERN.search(text):
        try:
            await message.delete()
            warn = await message.reply_text(
                f"⚠️ {message.from_user.mention}, **Sharing Links or Usernames (@mentions) is strictly not allowed in this group!**"
            )
            await asyncio.sleep(8)
            await warn.delete()
        except Exception as e:
            print(f"Link Delete Error: {e}")

@Client.on_callback_query(filters.regex(r"^(app_grp_|rej_grp_)"))
async def group_approval_callback(client, query):
    if query.from_user.id != ADMIN_ID:
        return await query.answer("❌ Access Denied! Admin only feature.", show_alert=True)
    
    action, chat_id = query.data.rsplit("_", 1)
    chat_id = int(chat_id)

    if action == "app_grp":
        await approve_chat_in_db(chat_id)
        await query.message.edit_text(f"{query.message.text.markdown}\n\n✅ **Status:** `Approved`")
        await query.answer("Group Approved Successfully!")
        try:
            await client.send_message(chat_id, "🎉 **Congratulations! This group has been Approved by the Bot Admin.**")
        except Exception:
            pass
    else:
        await remove_approved_chat(chat_id)
        await query.message.edit_text(f"{query.message.text.markdown}\n\n❌ **Status:** `Rejected & Left`")
        await query.answer("Group Rejected!")
        try:
            await client.leave_chat(chat_id)
        except Exception:
            pass
                      
