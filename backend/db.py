from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def connect_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    return client["envirolink"]