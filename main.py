from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# প্লাগইন লোড করার কনফিগারেশন
plugins = dict(root="bot/plugins")

app = Client(
    "movie_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=plugins # এটি স্বয়ংক্রিয়ভাবে plugins ফোল্ডারের সব ফাইল লোড করবে
)

if __name__ == "__main__":
    print("বটটি চালু হচ্ছে...")
    app.run()
