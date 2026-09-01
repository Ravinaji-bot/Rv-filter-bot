import motor.motor_asyncio
import logging
from info import DATABASE_URI, DATABASE_NAME
from utils import clean_file_name

client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URI, 
    maxPoolSize=100, 
    minPoolSize=10, 
    maxIdleTimeMS=50000
)
db = client[DATABASE_NAME]
files_col = db.files
approved_chats_col = db.approved_chats
banned_users_col = db.banned_users
requests_col = db.requests
users_col = db.users
manual_filters_col = db.manual_filters

async def create_db_indexes():
    try:
        await files_col.create_index([("file_name", "text")], name="filename_text_idx")
        await files_col.create_index("file_id", unique=True)
        await manual_filters_col.create_index([("chat_id", 1), ("keyword", 1)], unique=True)
        logging.info("⚡ MongoDB Text & Manual Filter Indexes Configured Successfully!")
    except Exception as e:
        logging.error(f"Index Error: {e}")

async def save_file_to_db(file_id: str, raw_file_name: str, file_size: int):
    cleaned_name = clean_file_name(raw_file_name)
    exists = await files_col.find_one({"file_id": file_id})
    if not exists:
        await files_col.insert_one({
            "file_name": cleaned_name,
            "file_id": file_id,
            "file_size": file_size
        })
        return True
    return False

async def get_search_results(query: str):
    try:
        cleaned_query = clean_file_name(query)
        cursor = files_col.find(
            {"$text": {"$search": cleaned_query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(10)
        
        results = await cursor.to_list(length=10)
        if not results:
            cursor = files_col.find({"file_name": {"$regex": cleaned_query, "$options": "i"}}).limit(10)
            results = await cursor.to_list(length=10)
            
        return results
    except Exception as e:
        logging.error(f"DB Search Error: {e}")
        return []

async def get_file_details(file_id: str):
    try:
        return await files_col.find_one({"file_id": file_id})
    except Exception as e:
        logging.error(f"DB Fetch Error: {e}")
        return None

async def get_all_file_titles():
    try:
        cursor = files_col.find({}, {"file_name": 1}).limit(500)
        titles = [doc["file_name"] async for doc in cursor if "file_name" in doc]
        return titles
    except Exception:
        return []

async def is_chat_approved(chat_id: int) -> bool:
    chat = await approved_chats_col.find_one({"chat_id": chat_id})
    return True if chat else False

async def approve_chat_in_db(chat_id: int):
    await approved_chats_col.update_one(
        {"chat_id": chat_id}, {"$set": {"status": "approved"}}, upsert=True
    )

async def remove_approved_chat(chat_id: int):
    await approved_chats_col.delete_one({"chat_id": chat_id})

async def ban_user_in_db(user_id: int):
    await banned_users_col.update_one(
        {"user_id": user_id}, {"$set": {"status": "banned"}}, upsert=True
    )

async def unban_user_in_db(user_id: int):
    await banned_users_col.delete_one({"user_id": user_id})

async def is_user_banned(user_id: int) -> bool:
    user = await banned_users_col.find_one({"user_id": user_id})
    return True if user else False

async def save_movie_request(user_id: int, user_name: str, movie_name: str):
    await requests_col.insert_one({
        "user_id": user_id,
        "user_name": user_name,
        "movie_name": movie_name,
        "status": "pending"
    })

async def add_user_to_db(user_id: int, user_name: str):
    exists = await users_col.find_one({"user_id": user_id})
    if not exists:
        await users_col.insert_one({"user_id": user_id, "user_name": user_name})
        return True
    return False

async def get_db_stats():
    try:
        total_files = await files_col.count_documents({})
        total_chats = await approved_chats_col.count_documents({})
        total_users = await users_col.count_documents({})
        total_manual_filters = await manual_filters_col.count_documents({})
        stats = await db.command("dbstats")
        data_size = stats.get("dataSize", 0) / (1024 * 1024)
        
        return {
            "total_files": total_files,
            "total_chats": total_chats,
            "total_users": total_users,
            "total_manual_filters": total_manual_filters,
            "db_size": f"{data_size:.2f} MB"
        }
    except Exception as e:
        logging.error(f"Stats DB Error: {e}")
        return {"total_files": 0, "total_chats": 0, "total_users": 0, "total_manual_filters": 0, "db_size": "0 MB"}

async def add_manual_filter(chat_id: int, keyword: str, text: str, file_id: str = None, media_type: str = None):
    keyword = keyword.lower().strip()
    filter_data = {
        "chat_id": chat_id,
        "keyword": keyword,
        "text": text,
        "file_id": file_id,
        "media_type": media_type
    }
    await manual_filters_col.update_one(
        {"chat_id": chat_id, "keyword": keyword},
        {"$set": filter_data},
        upsert=True
    )

async def get_manual_filter(chat_id: int, keyword: str):
    keyword = keyword.lower().strip()
    return await manual_filters_col.find_one({"chat_id": chat_id, "keyword": keyword})

async def delete_manual_filter(chat_id: int, keyword: str) -> bool:
    keyword = keyword.lower().strip()
    result = await manual_filters_col.delete_one({"chat_id": chat_id, "keyword": keyword})
    return result.deleted_count > 0

async def get_all_manual_filters(chat_id: int):
    cursor = manual_filters_col.find({"chat_id": chat_id})
    return await cursor.to_list(length=100)
