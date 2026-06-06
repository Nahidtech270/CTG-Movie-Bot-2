from pyrogram import Client, filters
from pyrogram.types import Message
import config
from database import save_file

# ১. অটো-ইনডেক্সিং (যেকোনো চ্যানেলে বট অ্যাডমিন থাকলে নতুন ফাইল আসলেই সেভ হবে)
@Client.on_message(filters.channel & (filters.document | filters.video))
async def auto_index(client: Client, message: Message):
    file = message.document or message.video
    await save_file(
        file_name=file.file_name,
        file_size=file.file_size,
        file_id=file.file_id,
        chat_id=message.chat.id,
        message_id=message.id
    )

# ২. বাল্ক ইনডেক্সিং (কোনো চ্যানেল থেকে মেসেজ ফরোয়ার্ড করলে পেছনের সব ফাইল ইনডেক্স হবে)
@Client.on_message(filters.forwarded & filters.private)
async def bulk_index(client: Client, message: Message):
    # শুধু অ্যাডমিনই এই কমান্ড ব্যবহার করতে পারবে
    if message.from_user.id != config.ADMIN_ID:
        return

    # ফরোয়ার্ড করা মেসেজটি কোনো চ্যানেল থেকে এসেছে কিনা তা নিশ্চিত করা
    if not message.forward_from_chat:
        await message.reply_text("দয়া করে একটি চ্যানেল থেকে মেসেজ ফরোয়ার্ড করুন।")
        return

    chat_id = message.forward_from_chat.id
    last_msg_id = message.forward_from_message_id

    status_msg = await message.reply_text("ইনডেক্সিং শুরু হচ্ছে... অনুগ্রহ করে অপেক্ষা করুন।")
    
    saved_count = 0
    # শেষ মেসেজ আইডি থেকে শুরু করে পেছনের ১০০০টি মেসেজ স্ক্যান করবে (প্রয়োজনে লিমিট বাড়ানো যাবে)
    async for msg in client.get_chat_history(chat_id, offset_id=last_msg_id + 1, limit=1000):
        if msg.document or msg.video:
            file = msg.document or msg.video
            saved = await save_file(
                file_name=file.file_name,
                file_size=file.file_size,
                file_id=file.file_id,
                chat_id=chat_id,
                message_id=msg.id
            )
            if saved:
                saved_count += 1

    await status_msg.edit_text(f"সফলভাবে ইনডেক্স সম্পন্ন হয়েছে!\nমোট {saved_count} টি নতুন ফাইল ডাটাবেজে সেভ হয়েছে।")
