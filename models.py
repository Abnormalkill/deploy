# models.py
from bson.objectid import ObjectId 
import datetime

# --- User Model ---
class User:
    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name
        
    @staticmethod
    def find_by_email(mongo, email):
        return mongo.db.users.find_one({"email": email})

    @staticmethod
    def find_by_id(mongo, user_id):
        try:
            return mongo.db.users.find_one({"_id": ObjectId(user_id)})
        except:
            return None

    def save_to_db(self, mongo):
        return mongo.db.users.insert_one({
            "email": self.email, 
            "password": self.password,
            "name": self.name 
        })

# --- Message Model ---
class Message:
    @staticmethod
    def save_message(mongo, sender_id, sender_email, content):
        return mongo.db.messages.insert_one({
            "sender_id": ObjectId(sender_id),
            "sender_email": sender_email,
            "content": content,
            "timestamp": datetime.datetime.utcnow()
        })
    
    @staticmethod
    def get_recent_messages(mongo, limit=50):
        return list(mongo.db.messages.find().sort("timestamp", -1).limit(limit))

# --- Material Model ---
class Material:
    @staticmethod
    def save_material(mongo, uploader_id, uploader_email, filename, file_url):
        return mongo.db.materials.insert_one({
            "uploader_id": ObjectId(uploader_id),
            "uploader_email": uploader_email,
            "filename": filename,
            "file_url": file_url,
            "timestamp": datetime.datetime.utcnow()
        })
    
    @staticmethod
    def get_all_materials(mongo):
        return list(mongo.db.materials.find().sort("timestamp", -1))