import logging
import asyncio
from pyrogram import Client
from info import API_ID, API_HASH, BOT_TOKEN, PORT
from database.ia_filterdb import create_db_indexes

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Bot(Client):
    def __init__(self):
        super().__init__(
            "Rv-Filter-Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins")
        )

    async def start(self):
        await super().start()
        await create_db_indexes()
        me = await self.get_me()
        logging.info(f"⚡ Bot Started Successfully as @{me.username}")

    async def stop(self, *args):
        await super().stop()
        logging.info("⚡ Bot Stopped Successfully")

if __name__ == "__main__":
    app = Bot()
    app.run()
  
