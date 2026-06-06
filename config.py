# config.py

API_ID = 1234567          # আপনার Telegram API ID (integer)
API_HASH = "your_api_hash_here"  # আপনার Telegram API Hash (string)
BOT_TOKEN = "your_bot_token_here"  # BotFather থেকে পাওয়া টোকেন
ADMIN_ID = 123456789      # আপনার নিজের টেলিগ্রাম ইউজার আইডি
MAIN_CHANNEL_ID = -1001234567890  # আপনার প্রধান চ্যানেলের আইডি

# --- ডাবল ডাটাবেজ কনফিগারেশন ---
DATABASE_URI = "mongodb+srv://..."  # আপনার ১ম (Primary) MongoDB লিঙ্ক
MULTIPLE_DB = True                 # ২য় ডাটাবেজ সচল করতে True রাখুন, না চাইলে False
DATABASE_URI2 = "mongodb+srv://..." # আপনার ২য় (Backup) MongoDB লিঙ্ক (ঐচ্ছিক)
