from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        f"হ্যালো {message.from_user.mention},\n"
        "আমি মুভি সার্চ বট। আপনার কাঙ্ক্ষিত মুভিটির নাম লিখে সার্চ করুন।"
    )
