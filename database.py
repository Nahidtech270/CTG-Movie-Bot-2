from motor.motor_asyncio import AsyncIOMotorClient
import config

# মঙ্গোডিবি কানেকশন সেটআপ
client = AsyncIOMotorClient(config.MONGO_URI)
db = client["movie_search_bot"]
files_col = db["files"]

# ডাটাবেজে নতুন ফাইল সেভ করার ফাংশন
async def save_file(file_name, file_size, file_id, chat_id, message_id):
    # একই ফাইল বারবার যাতে সেভ না হয়, তার জন্য চেক করা
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

# ডাটাবেজ থেকে মুভি সার্চ করার ফাংশন
async def search_db(query):
    results = []
    # কেস-ইনসেনসিটিভ সার্চ (বড় বা ছোট হাতের অক্ষরের তফাৎ করবে না)
    cursor = files_col.find({"file_name": {"$regex": query, "$options": "i"}}).limit(20)
    async for doc in cursor:
        results.append(doc)
    return results
