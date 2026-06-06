# database.py

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import config

client = AsyncIOMotorClient(config.MONGO_URI)
db = client["movie_search_bot"]
files_col = db["files"]
users_col = db["users"]

# নতুন ইউজার সেভ (নিরাপদ করা হয়েছে)
async def add_user(user_id, username, first_name):
    # ইউজারনেম খালি থাকলে None এর বদলে 'No Username' সেভ হবে
    username = username if username else "No Username"
    first_name = first_name if first_name else "User"
    
    exists = await users_col.find_one({"user_id": user_id})
    if not exists:
        await users_col.insert_one({
            "user_id": user_id,
            "username": username,
            "first_name": first_name
        })

async def save_file(file_name, file_size, file_id, chat_id, message_id):
    exists = await files_col.find_one({"file_id": file_id})
    if not exists:
        file_data = {
            "file_name": file_name,
            "file_size": file_size,
            "file_id": file_id,
            "chat_id": chat_id,
            "message_id": message_id
        }
        await files_col.insert_one(file_data)
        return True
    return False

async def search_db(query):
    results = []
    cursor = files_col.find({"file_name": {"$regex": query, "$options": "i"}}).limit(20)
    async for doc in cursor:
        results.append(doc)
    return results

async def get_file_by_db_id(db_id):
    try:
        return await files_col.find_one({"_id": ObjectId(db_id)})
    except Exception:
        return None

async def get_stats():
    total_files = await files_col.estimated_document_count()
    total_users = await users_col.estimated_document_count()
    return total_files, total_users

# --- এডমিনদের জন্য ডিলিট করার নতুন ফাংশনসমূহ ---

# ক. নির্দিষ্ট নাম দিয়ে এক বা একাধিক ফাইল ডিলিট
async def delete_files_by_name(query):
    result = await files_col.delete_many({"file_name": {"$regex": query, "$options": "i"}})
    return result.deleted_count

# খ. সম্পূর্ণ ডাটাবেজ ডিলিট (রিসেট)
async def delete_all_files_from_db():
    result = await files_col.delete_many({})
    return result.deleted_count
