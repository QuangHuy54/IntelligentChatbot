#from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import AsyncMongoClient

import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "assistantdb")

client = AsyncMongoClient(MONGO_URL)
db = client[MONGO_DB]

threads_collection = db["threads"]
messages_collection = db["messages"]