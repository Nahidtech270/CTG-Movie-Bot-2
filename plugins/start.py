# plugins/start.py

from pyrogram import Client, filters
from pyrogram.types import Message
from database import add_user, get_stats

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    try:
        # ইউজার সেভ করার সময় এরর হ্যান্ডেল করা
        await add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
    except Exception as e:
        print(f"User save error: {e}")
        
    try:
        total_files, total_users = await get_stats()
    except Exception as e:
        print(f"Stats fetch error: {e}")
        total_files, total_users = 0, 0
    
    welcome_text = (
        f"👋 **হ্যালো {message.from_user.first_name or 'User'}!**\n\n"
        f"🎬 **CTG Movie সার্চ বটে আপনাকে স্বাগতম!**\n\n"
        f"📢 **কিভাবে মুভি খুঁজবেন?**\n"
        f"বটের ইনবক্সে সরাসরি যেকোনো মুভির নাম লিখে মেসেজ পাঠান।\n"
        f"💡 *যেমন:* `RRR` অথবা `KGF` লিখে পাঠান।\n\n"
        f"📊 **আমাদের বর্তমান ডাটাবেজ:**\n"
        f"📁 মোট মুভি ফাইল: `{total_files}` টি\n"
        f"👥 মোট সক্রিয় ইউজার: `{total_users}` জন\n\n"
        f"⚠️ *মুভির সঠিক বানান লেখার অনুরোধ রইল।*"
    )
    await message.reply_text(welcome_text)
