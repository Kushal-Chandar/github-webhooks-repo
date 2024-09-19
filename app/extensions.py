from pymongo import MongoClient
import os

mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)
db = client["events"]
events_collection = db["github_webhooks"]
