# plugins/admin.py

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import config
# database থেকে প্রিমিয়াম হ্যান্ডলিংয়ের নতুন ফাংশনগুলো ইম্পোর্ট করা হয়েছে
from database import (
    get_stats, 
    delete_files_by_name, 
    delete_all_files_from_db, 
    get_all_users,
    add_premium_user,       # নতুন ফাংশন
    remove_premium_user,    # নতুন ফাংশন
    get_all_premium_users   # নতুন ফাংশন
)

# একক এডমিনের পরিবর্তে মাল্টিপল এডমিন ফিল্টার (config.ADMINS তালিকা চেক করবে)
is_admin = filters.create(lambda _, __, message: message.from_user and message.from_user.id in config.ADMINS)

@Client.on_message(filters.command("stats") & is_admin)
async def stats_cmd(client: Client, message: Message):
    total_files, total_users = await get_stats()
    await message.reply_text(
        f"📊 **বটের লাইভ স্ট্যাটাস:**\n\n"
        f"👥 মোট ইউজার: `{total_users}` জন\n"
        f"📁 মোট মুভি ফাইল: `{total_files}` টি"
    )

@Client.on_message(filters.command("delete") & is_admin)
async def delete_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ **সঠিক নিয়ম:** `/delete [মুভির নাম]` লিখে পাঠান।")
        return
    query = " ".join(message.command[1:])
    deleted_count = await delete_files_by_name(query)
    await message.reply_text(f"✅ ডাটাবেজ থেকে **'{query}'** নামের মোট `{deleted_count}` টি ফাইল ডিলিট করা হয়েছে।")

@Client.on_message(filters.command("clean_database") & is_admin)
async def clean_database_cmd(client: Client, message: Message):
    deleted_count = await delete_all_files_from_db()
    await message.reply_text(f"🛑 **ডাটাবেজ সম্পূর্ণ খালি করা হয়েছে!**\nমোট `{deleted_count}` টি ফাইল স্থায়ীভাবে মুছে ফেলা হয়েছে।")

@Client.on_message(filters.command("broadcast") & is_admin)
async def broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ **ব্যবহার বিধি:** যেকোনো মেসেজ বা পোস্টের ওপর রিপ্লাই দিয়ে লিখুন `/broadcast`")
        return
    status_msg = await message.reply_text("📢 ব্রডকাস্ট শুরু হচ্ছে...")
    users = await get_all_users()
    success = 0
    failed = 0
    for user_id in users:
        try:
            await message.reply_to_message.copy(chat_id=user_id)
            success += 1
            await asyncio.sleep(0.3)
        except Exception:
            failed += 1
    await status_msg.edit_text(
        f"📢 **ব্রডকাস্ট সফলভাবে সম্পন্ন হয়েছে!**\n\n"
        f"✅ সফলভাবে পাঠানো হয়েছে: `{success}` জন ইউজারকে\n"
        f"❌ ব্যর্থ হয়েছে (বট ব্লক করেছে): `{failed}` জন ইউজার"
    )

# --- নতুন প্রিমিয়াম নিয়ন্ত্রণ কমান্ডসমূহ ---

# ১. প্রিমিয়াম ইউজার যুক্ত করার কমান্ড
@Client.on_message(filters.command("add_premium") & is_admin)
async def add_premium_cmd(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("⚠️ **ব্যবহার বিধি:** `/add_premium [User_ID]` অথবা যেকোনো ইউজারের মেসেজে রিপ্লাই দিয়ে লিখুন `/add_premium`")
        return
    
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("⚠️ **ভুল আইডি!** দয়া করে সঠিক সংখ্যাসূচক ইউজার আইডি দিন।")
            return
    
    # ডেটাবেজে প্রিমিয়াম স্ট্যাটাস আপডেট করা
    await add_premium_user(user_id)
    await message.reply_text(f"👑 **সফল হয়েছে!**\nইউজার আইডি `{user_id}` কে সফলভাবে প্রিমিয়াম (VIP) মেম্বার হিসেবে যুক্ত করা হয়েছে।")

# ২. প্রিমিয়াম ইউজার রিমুভ করার কমান্ড
@Client.on_message(filters.command("remove_premium") & is_admin)
async def remove_premium_cmd(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("⚠️ **ব্যবহার বিধি:** `/remove_premium [User_ID]` অথবা যেকোনো ইউজারের মেসেজে রিপ্লাই দিয়ে লিখুন `/remove_premium`")
        return
    
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text("⚠️ **ভুল আইডি!** দয়া করে সঠিক সংখ্যাসূচক ইউজার আইডি দিন।")
            return
    
    # ডেটাবেজ থেকে প্রিমিয়াম স্ট্যাটাস বাতিল করা
    await remove_premium_user(user_id)
    await message.reply_text(f"❌ **রিমুভ করা হয়েছে!**\nইউজার আইডি `{user_id}` কে সফলভাবে প্রিমিয়াম মেম্বারশিপ থেকে বাদ দেওয়া হয়েছে।")

# ৩. প্রিমিয়াম ইউজারদের তালিকা দেখার কমান্ড
@Client.on_message(filters.command("premiums") & is_admin)
async def premiums_list_cmd(client: Client, message: Message):
    premium_users = await get_all_premium_users()
    if not premium_users:
        await message.reply_text("ℹ️ বর্তমানে ডাটাবেজে কোনো প্রিমিয়াম ইউজার যুক্ত নেই।")
        return
    
    text = "👑 **প্রিমিয়াম (VIP) ইউজারদের তালিকা:**\n\n"
    for idx, u_id in enumerate(premium_users, 1):
        text += f"{idx}. `{u_id}`\n"
    await message.reply_text(text)
