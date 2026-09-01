import logging
import asyncio
from pyrogram import Client, enums, idle
from info import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL
from database.ia_filterdb import create_db_indexes

logging.basicConfig(level=logging.INFO)

app = Client(
    "AutoFilterBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
    parse_mode=enums.ParseMode.MARKDOWN
)

async def main():
    await app.start()
    await create_db_indexes()
    
    bot_info = await app.get_me()
    print(f"🚀 Bot Started Successfully: @{bot_info.username}")
    
    if LOG_CHANNEL:
        try:
            startup_text = (
                "🟢 **Bot Status Notification**\n\n"
                f"🤖 **Bot Name:** {bot_info.first_name}\n"
                f"🆔 **Bot Username:** @{bot_info.username}\n"
                "⚡ **Status:** `Healthy & Operational`\n"
                "🚀 **Engine:** Pyrogram Engine Online"
            )
            await app.send_message(chat_id=LOG_CHANNEL, text=startup_text)
            logging.info("✅ Startup notification sent to Log Channel!")
        except Exception as e:
            logging.error(f"Failed to send startup log: {e}")

    await idle()
    await app.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
