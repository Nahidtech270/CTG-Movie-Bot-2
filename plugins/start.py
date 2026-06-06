# plugins/start.py

from pyrogram import Client, filters
from pyrogram.types import Message
from database import add_user, get_stats

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    # ইউজারকে ডাটাবেজে যুক্ত করা হচ্ছে
    await add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    # ডাটাবেজ থেকে লাইভ স্ট্যাটাস নেওয়া হচ্ছে
    total_files, total_users = await get_stats()
    
    # একটি প্রফেশনাল ওয়েলকাম মেসেজ টেমপ্লেট
    welcome_text = (
        f"👋 **হ্যালো {message.from_user.first_name}!**\n\n"
        f"🎬 **CTG Movie সার্চ বটে আপনাকে স্বাগতম!**\n"
        f"এখানে আপনি আপনার পছন্দের যেকোনো মুভি ও ওয়েব সিরিজ পেয়ে যাবেন খুবই দ্রুত।\n\n"
        f"📢 **কিভাবে ব্যবহার করবেন?**\n"
        f"বটের ইনবক্সে সরাসরি যেকোনো মুভির নাম লিখে মেসেজ পাঠান।\n"
        f"💡 *উদাহরণ:* `RRR` অথবা `Money Heist` লিখে পাঠান।\n\n"
        f"📊 **আমাদের বর্তমান ডাটাবেজ স্ট্যাটাস:**\n"
        f"📁 মোট ইনডেক্সকৃত ফাইল: `{total_files}` টি\n"
        f"👥 আমাদের সাথে যুক্ত আছেন: `{total_users}` জন ইউজার\n\n"
        f"⚠️ *সঠিক ফলাফল পেতে মুভির বানানটি সঠিকভাবে লেখার অনুরোধ রইল।*"
    )
    
    await message.reply_text(welcome_text)
