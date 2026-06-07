# database.py

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import config
import re
import difflib  # সর্টিং বা সাজানোর জন্য এটি ইম্পোর্ট করা হয়েছে

client1 = AsyncIOMotorClient(config.DATABASE_URI)
db1 = client1["movie_search_bot"]
files_col1 = db1["files"]
users_col = db1["users"]
requests_col = db1["requests"]

client2 = None
files_col2 = None
if config.MULTIPLE_DB and config.DATABASE_URI2:
    client2 = AsyncIOMotorClient(config.DATABASE_URI2)
    db2 = client2["movie_search_bot"]
    files_col2 = db2["files"]

async def get_active_files_collection():
    if not config.MULTIPLE_DB or not files_col2:
        return files_col1
    try:
        stats = await db1.command("dbstats")
        data_size_mb = stats.get("dataSize", 0) / (1024 * 1024)
        if data_size_mb > 100:
            return files_col2
    except Exception as e:
        print(f"Primary DB Check Failed: {e}")
    return files_col1

async def add_user(user_id, username, first_name):
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
    active_col = await get_active_files_collection()
    
    # ডুপ্লিকেট চেক
    exists = await active_col.find_one({
        "$or": [
            {"file_id": file_id},
            {"file_name": file_name, "file_size": file_size}
        ]
    })
    
    if not exists:
        file_data = {
            "file_name": file_name,
            "file_size": file_size,
            "file_id": file_id,
            "chat_id": chat_id,
            "message_id": message_id
        }
        await active_col.insert_one(file_data)
        return True
        
    return False

# অ্যান্ড সার্চ ও রিয়েল-টাইম সর্টিং লজিক
async def search_db(query):
    words = query.strip().split()
    if not words:
        return []
    
    regex_list = [{"file_name": {"$regex": re.escape(w), "$options": "i"}} for w in words]
    query_filter = {"$and": regex_list} if len(regex_list) > 1 else regex_list[0]
    
    results = []
    cursor1 = files_col1.find(query_filter).limit(30)
    async for doc in cursor1:
        results.append(doc)
        
    if config.MULTIPLE_DB and files_col2:
        cursor2 = files_col2.find(query_filter).limit(30)
        async for doc in cursor2:
            if not any(d['file_id'] == doc['file_id'] for d in results):
                results.append(doc)
                
    # --- স্মার্ট সর্টিং অ্যালগরিদম (যা আসল মুভিটি সবার উপরে নিয়ে আসবে) ---
    def get_sort_key(doc):
        name = doc["file_name"].lower()
        q = query.lower()
        
        # ১. হুবহু মিললে (Exact Match) সবার আগে থাকবে (Priority 0)
        if q == name:
            return 0
        # ২. সার্চের নাম দিয়ে শুরু হলে (Starts With) ২য় স্থানে থাকবে (Priority 1)
        if name.startswith(q):
            return 1
        # ৩. সিমিলার নামের ফাইলগুলো ক্লোজনেসের হার অনুযায়ী সাজানো হবে (Priority 1.X থেকে 2)
        ratio = difflib.SequenceMatcher(None, q, name).ratio()
        return 2 - ratio

    # পাইথনের দ্রুতগতির ইন-প্লেস সর্টিং ব্যবহার করা হয়েছে
    results.sort(key=get_sort_key)
    
    return results

async def get_file_by_db_id(db_id):
    try:
        file_data = await files_col1.find_one({"_id": ObjectId(db_id)})
        if not file_data and config.MULTIPLE_DB and files_col2:
            file_data = await files_col2.find_one({"_id": ObjectId(db_id)})
        return file_data
    except Exception:
        return None

async def get_stats():
    total_files = await files_col1.estimated_document_count()
    if config.MULTIPLE_DB and files_col2:
        total_files += await files_col2.estimated_document_count()
    total_users = await users_col.estimated_document_count()
    return total_files, total_users

async def delete_files_by_name(query):
    count = await files_col1.delete_many({"file_name": {"$regex": query, "$options": "i"}})
    deleted = count.deleted_count
    if config.MULTIPLE_DB and files_col2:
        count2 = await files_col2.delete_many({"file_name": {"$regex": query, "$options": "i"}})
        deleted += count2.deleted_count
    return deleted

async def delete_all_files_from_db():
    count = await files_col1.delete_many({})
    deleted = count.deleted_count
    if config.MULTIPLE_DB and files_col2:
        count2 = await files_col2.delete_many({})
        deleted += count2.deleted_count
    return deleted

async def get_all_users():
    users = []
    cursor = users_col.find({})
    async for doc in cursor:
        users.append(doc["user_id"])
    return users

async def save_movie_request(user_id, query):
    exists = await requests_col.find_one({"user_id": user_id, "query": query, "status": "pending"})
    if not exists:
        await requests_col.insert_one({
            "user_id": user_id,
            "query": query,
            "status": "pending"
        })
        return True
    return False
