# bot.py

import asyncio

# পাইথনের নতুন ভার্সনে Pyrogram এর ইভেন্ট লুপ এরর এড়ানোর জন্য এই কোডটুকু অবশ্যই শুরুতে রাখতে হবে
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# এরপরে বাকি জিনিসগুলো ইম্পোর্ট হবে
from pyrogram import Client
import config

# প্লাগইন লোডার কনফিগারেশন
plugins = dict(root="plugins")

app = Client(
    "movie_search_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=plugins
)

if __name__ == "__main__":
    print("অভিনন্দন! আপনার মুভি বটটি সফলভাবে চালু হয়েছে।")
    app.run()
