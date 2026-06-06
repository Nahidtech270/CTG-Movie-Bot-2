# database.py

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId  # এটি নতুন যোগ করা হয়েছে
import config

client = AsyncIOMotorClient(config.MONGO_URI)
db = client["movie_search_bot"]
files_col = db["files"]

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

# নতুন ফাংশন: ছোট ডাটাবেজ আইডি দিয়ে ফাইল খোঁজার জন্য
async def get_file_by_db_id(db_id):
    try:
        # string আইডিকে মঙ্গোডিবির ObjectId-তে রূপান্তর করা
        return await files_col.find_one({"_id": ObjectId(db_id)})
    except Exception:
        return None
