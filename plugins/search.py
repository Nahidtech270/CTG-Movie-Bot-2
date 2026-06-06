# plugins/search.py

import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from pyrogram.enums import ChatType
from pyrogram.errors import UserNotParticipant
from database import search_db, get_file_by_db_id, add_user
import config

FILES_PER_PAGE = 5

# --- প্রফেশনাল ক্লিন-আপ ফাংশন (মুভির নাম ঠিক রেখে প্রমোশন লিংক ডিলিট করবে) ---
def clean_movie_title(name: str) -> str:
    name = re.sub(r'@[a-zA-Z0-9_]+', '', name)
    name = re.sub(r'(https?://)?(t\.me|telegram\.me|telegram\.dog)/[a-zA-Z0-9_\+]+', '', name)
    domain_extensions = "com|org|net|xyz|club|co|tv|link|info|me|cc|site|space|click|in|online|icu"
    name = re.sub(r'\b[a-zA-Z0-9-]+\.(' + domain_extensions + r')\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*-\s*$', '', name)
    name = name.replace("__", "_").replace("..", ".").replace("  ", " ")
    if not name.strip():
         name = "Movie File"
    return name.strip()

# --- ৫ মিনিট পর ফাইল স্বয়ংক্রিয়ভাবে মুছে দেওয়ার ব্যাকগ্রাউন্ড টাস্ক ---
async def auto_delete_file(message: Message):
    await asyncio.sleep(300) # ৩০০ সেকেন্ড = ৫ মিনিট
    try:
        await message.delete()
    except Exception as e:
        print(f"Failed to auto delete file: {e}")

# --- গ্রুপে বটের রিপ্লাই ১ মিনিট পর ডিলিট করার ব্যাকগ্রাউন্ড টাস্ক ---
async def auto_delete_group_reply(message: Message):
    await asyncio.sleep(60) # ৬০ সেকেন্ড = ১ মিনিট
    try:
        await message.delete()
    except:
        pass


@Client.on_message(filters.text)
async def main_handler(client: Client, message: Message):
    text = message.text.strip()

    # ==========================================
    # --- ক. পার্সোনাল চ্যাট হ্যান্ডলার (Private PM) ---
    # ==========================================
    if message.chat.type == ChatType.PRIVATE:
        if text.startswith("/start"):
            
            # --- ১. ফোর্স সাবস্ক্রিপশন চেক (ইউজারকে চ্যানেলে জয়েন থাকতেই হবে) ---
            try:
                await client.get_chat_member(config.MAIN_CHANNEL_ID, message.from_user.id)
            except UserNotParticipant:
                # ইউজার চ্যানেলে জয়েন না থাকলে জয়েন বাটন এবং ট্রাই-এগেইন বাটন দেখানো হবে
                fsub_buttons = [
                    [InlineKeyboardButton("🍿 Join Our Movie Channel", url=config.CHANNEL_LINK_1)],
                    [InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{config.BOT_USERNAME}?start={text[7:]}" if len(text.split()) > 1 else f"https://t.me/{config.BOT_USERNAME}?start=start")]
                ]
                await message.reply_text(
                    f"👋 **হ্যালো {message.from_user.first_name}!**\n\n"
                    f"বট থেকে ফাইল পেতে হলে আপনাকে প্রথমে আমাদের মুভি চ্যানেলে জয়েন হতে হবে।\n\n"
                    f"👉 অনুগ্রহ করে নিচের বাটনে ক্লিক করে জয়েন করুন এবং 'Try Again' বাটনে ক্লিক করুন।",
                    reply_markup=InlineKeyboardMarkup(fsub_buttons)
                )
                return
            except Exception as e:
                print(f"FSub Error: {e}")

            # --- ২. মিনি অ্যাপ থেকে ফিরে আসলে ফাইল পাঠানো ও ৫ মিনিটের ডিলিট শিডিউল ---
            if len(text.split()) > 1:
                file_db_id = text.split()[1]
                file_data = await get_file_by_db_id(file_db_id)
                
                if file_data:
                    try:
                        raw_name = file_data["file_name"]
                        cleaned_name = clean_movie_title(raw_name)
                        file_size = round(file_data["file_size"] / (1024 * 1024), 2)
                        
                        caption_text = (
                            f"🎬 **ফাইলের নাম:** `{cleaned_name}`\n"
                            f"💾 **ফাইলের সাইজ:** `{file_size} MB`\n\n"
                            f"📢 **চ্যানেল লিংকসমূহ নিচে দেওয়া হলো:**\n"
                            f"👉 আমাদের সাথে ব্যাকআপ চ্যানেলে যুক্ত থাকুন।\n\n"
                            f"⚠️ **নিরাপত্তা সতর্কবার্তা:**\n"
                            f"কপিরাইট এড়াতে এই ফাইলটি আগামী **৫ মিনিট** পর স্বয়ংক্রিয়ভাবে মুছে যাবে। দয়া করে এর মধ্যেই আপনার সেভড মেসেজে ফাইলটি ফরওয়ার্ড করে রাখুন।"
                        )
                        
                        promo_buttons = [
                            [InlineKeyboardButton("🍿 All Movie Link", url=config.CHANNEL_LINK_1)],
                            [InlineKeyboardButton("📢 Join Backup Channel", url=config.CHANNEL_LINK_2)]
                        ]
                        
                        sent_file = await client.send_cached_media(
                            chat_id=message.chat.id,
                            file_id=file_data["file_id"],
                            caption=caption_text,
                            reply_markup=InlineKeyboardMarkup(promo_buttons)
                        )
                        
                        asyncio.create_task(auto_delete_file(sent_file))
                        
                    except Exception as e:
                        await message.reply_text(f"❌ দুঃখিত, ফাইলটি পাঠানো যাচ্ছে না: {str(e)}")
                else:
                    await message.reply_text("❌ দুঃখিত, ফাইলটি ডাটাবেজে খুঁজে পাওয়া যায়নি!")
                return

            # সাধারণ স্টার্ট হলে
            try:
                await add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
            except:
                pass

            welcome_text = (
                f"👋 **হ্যালো {message.from_user.first_name or 'ইউজার'}!**\n\n"
                f"🎬 **CTG Movie সার্চ বটে আপনাকে স্বাগতম!**\n"
                f"বটের ইনবক্সে সরাসরি যেকোনো মুভির নাম লিখে মেসেজ পাঠান।"
            )
            await message.reply_text(welcome_text)
            return

        if text.startswith("/"):
            return

        # সাধারণ সার্চ কুয়েরি (PM চ্যাটে)
        query = text
        search_msg = await message.reply_text("🔍 খোঁজা হচ্ছে... অনুগ্রহ করে অপেক্ষা করুন।")
        results = await search_db(query)
        
        if not results:
            await search_msg.edit_text(f"❌ দুঃখিত, **'{query}'** নামের কোনো ফাইল পাওয়া যায়নি।")
            return

        await search_msg.delete()
        await send_search_results(message, results, query, page=0)

    # ==========================================
    # --- খ. গ্রুপ চ্যাট হ্যান্ডলার (Auto-Filter Group Mode) ---
    # ==========================================
    elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        if text.startswith("/"):
            return # গ্রুপে কমান্ড ইগনোর করবে
            
        query = text
        results = await search_db(query)
        
        if not results:
            return # গ্রুপে মুভি না পাওয়া গেলে বট শান্ত থাকবে (যাতে গ্রুপে স্প্যাম না হয়)
            
        # গ্রুপে প্রথম ৫টি মুভি বাটন আকারে সাজানো হবে (ইউজার-লকড মেকানিজম)
        # callback_data স্ট্রাকচার: gfile|file_db_id|searcher_user_id
        buttons = []
        for file in results[:5]:
            file_name = clean_movie_title(file["file_name"])
            file_size = round(file["file_size"] / (1024 * 1024), 2)
            db_id = str(file["_id"])
            searcher_id = message.from_user.id
            
            buttons.append([InlineKeyboardButton(
                text=f"🎬 {file_name} [{file_size} MB]",
                callback_data=f"gfile|{db_id}|{searcher_id}"
            )])
            
        text_reply = (
            f"🍿 **{message.from_user.mention}** এর খোঁজা মুভিটির **{len(results)}** টি রেজাল্ট পাওয়া গেছে।\n"
            f"👇 মুভি ফাইলটি সরাসরি আপনার ইনবক্সে পেতে নিচের বাটনে ক্লিক করুন:\n\n"
            f"⚠️ *এই মেসেজটি ১ মিনিট পর ডিলিট হয়ে যাবে।*"
        )
        
        group_reply = await message.reply_text(text_reply, reply_markup=InlineKeyboardMarkup(buttons))
        
        # ১ মিনিট পর গ্রুপ মেসেজ ডিলিট
        asyncio.create_task(auto_delete_group_reply(group_reply))


# সার্চ রেজাল্ট পেজ আকারে সাজানোর ফাংশন (PM চ্যাটের জন্য)
async def send_search_results(message_or_query, results, query, page=0):
    total_results = len(results)
    start_index = page * FILES_PER_PAGE
    end_index = start_index + FILES_PER_PAGE
    
    current_page_results = results[start_index:end_index]
    
    raw_url = config.WEB_URL.strip()
    if raw_url.lower().startswith("https://"):
        raw_url = raw_url[8:]
    elif raw_url.lower().startswith("http://"):
        raw_url = raw_url[7:]
    if raw_url.endswith("/"):
        raw_url = raw_url[:-1]
    
    buttons = []
    for file in current_page_results:
        file_name = clean_movie_title(file["file_name"])
        file_size = round(file["file_size"] / (1024 * 1024), 2)
        db_id = str(file["_id"])
        
        web_app_url = f"https://{raw_url}/download?id={db_id}"
        
        buttons.append([InlineKeyboardButton(
            text=f"🎬 {file_name} [{file_size} MB]",
            web_app=WebAppInfo(url=web_app_url)
        )])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ আগের", callback_data=f"page|{page - 1}|{query}"))
    
    total_pages = (total_results + FILES_PER_PAGE - 1) // FILES_PER_PAGE
    nav_buttons.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="pages_info"))
    
    if end_index < total_results:
        nav_buttons.append(InlineKeyboardButton("পরের ▶️", callback_data=f"page|{page + 1}|{query}"))
        
    if nav_buttons:
        buttons.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(buttons)
    text = f"🍿 **'{query}'** এর জন্য প্রাপ্ত ফলাফলসমূহ:"
    
    if isinstance(message_or_query, Message):
        await message_or_query.reply_text(text, reply_markup=reply_markup)
    else:
        await message_or_query.message.edit_text(text, reply_markup=reply_markup)


# ==========================================
# --- গ. কলব্যাক কুয়েরি হ্যান্ডলার (Callback Handler) ---
# ==========================================

# ১. পেজ নেভিগেশন (PM চ্যাটের জন্য)
@Client.on_callback_query(filters.regex(r"^page\|"))
async def page_click_handler(client: Client, callback_query):
    data = callback_query.data.split("|")
    target_page = int(data[1])
    query = data[2]
    
    results = await search_db(query)
    if results:
        await send_search_results(callback_query, results, query, page=target_page)
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^pages_info$"))
async def pages_info_click(client: Client, callback_query):
    await callback_query.answer("এটি বর্তমান পেজ নম্বর নির্দেশ করছে।", show_alert=False)

# ২. গ্রুপ ফাইল ক্লিক ভেরিফিকেশন (ইউজার-লকড ব্যাকগ্রাউন্ড হ্যান্ডলিং)
@Client.on_callback_query(filters.regex(r"^gfile\|"))
async def group_file_click_handler(client: Client, callback_query):
    data = callback_query.data.split("|")
    file_db_id = data[1]
    searcher_id = int(data[2])
    clicker_id = callback_query.from_user.id

    # যদি অন্য কেউ বাটনে ক্লিক করে (ইউজার লক অ্যালার্ট)
    if clicker_id != searcher_id:
        await callback_query.answer(
            "⚠️ দুঃখিত! এই সার্চ রেজাল্টটি আপনার জন্য নয়। অনুগ্রহ করে নিজে গ্রুপে মুভির নাম লিখে সার্চ করুন।", 
            show_alert=True
        )
        return

    # আসল ইউজার ক্লিক করলে তাকে বটের ইনবক্সে রিডাইরেক্ট করা
    await callback_query.answer(
        url=f"https://t.me/{config.BOT_USERNAME}?start={file_db_id}"
    )
