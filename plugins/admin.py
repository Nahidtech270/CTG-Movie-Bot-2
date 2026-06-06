# plugins/admin.py

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import config
from database import get_stats, delete_files_by_name, delete_all_files_from_db, get_all_users

is_admin = filters.user(config.ADMIN_ID)

# ১. লাইভ স্ট্যাটাস দেখার কমান্ড
@Client.on_message(filters.command("stats") & is_admin)
async def stats_cmd(client: Client, message: Message):
    total_files, total_users = await get_stats()
    await message.reply_text(
        f"📊 **বটের লাইভ স্ট্যাটাস:**\n\n"
        f"👥 মোট ইউজার: `{total_users}` জন\n"
        f"📁 মোট মুভি ফাইল: `{total_files}` টি"
    )

# ২. নাম দিয়ে মুভি ডিলিট করার কমান্ড
@Client.on_message(filters.command("delete") & is_admin)
async def delete_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ **সymmetrical rule:** `/delete [মুভির নাম]` লিখে পাঠান।")
        return
        
    query = " ".join(message.command[1:])
    deleted_count = await delete_files_by_name(query)
    await message.reply_text(f"✅ ডাটাবেজ থেকে **'{query}'** নামের মোট `{deleted_count}` টি ফাইল ডিলিট করা হয়েছে।")

# ৩. সম্পূর্ণ ডাটাবেজ ডিলিট (অল ডিলিট) করার কমান্ড
@Client.on_message(filters.command("clean_database") & is_admin)
async def clean_database_cmd(client: Client, message: Message):
    deleted_count = await delete_all_files_from_db()
    await message.reply_text(f"🛑 **ডাটাবেজ সম্পূর্ণ খালি করা হয়েছে!**\nমোট `{deleted_count}` টি ফাইল স্থায়ীভাবে মুছে ফেলা হয়েছে।")

# ৪. গ্লোবাল ব্রডকাস্ট কমান্ড (সব ইউজারকে একসাথে মেসেজ বা ফাইল পাঠানোর জন্য)
# ব্যবহার বিধি: যেকোনো মেসেজে রিপ্লাই দিয়ে লিখুন /broadcast
@Client.on_message(filters.command("broadcast") & is_admin)
async def broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ **ব্যবহার বিধি:** যেকোনো মেসেজ বা পোস্টের ওপর রিপ্লাই দিয়ে লিখুন `/broadcast`")
        return
        
    status_msg = await message.reply_text("📢 ব্রডকাস্ট শুরু হচ্ছে... অনুগ্রহ করে ব্যাকগ্রাউন্ড প্রসেসটি শেষ হতে দিন।")
    users = await get_all_users()
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            # রিপ্লাই করা মেসেজটি হুবহু কপি করে ইউজারের ইনবক্সে পাঠানো হচ্ছে
            await message.reply_to_message.copy(chat_id=user_id)
            success += 1
            await asyncio.sleep(0.3) # টেলিগ্রাম এপিআই ফ্ল্যাড লিমিট এড়াতে বিরতি
        except Exception:
            failed += 1
            
    await status_msg.edit_text(
        f"📢 **ব্রডকাস্ট সফলভাবে সম্পন্ন হয়েছে!**\n\n"
        f"✅ সফলভাবে পাঠানো হয়েছে: `{success}` জন ইউজারকে\n"
        f"❌ ব্যর্থ হয়েছে (বট ব্লক করেছে): `{failed}` জন ইউজার"
    )
