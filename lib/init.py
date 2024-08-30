import logging as log

from pymongo import MongoClient

BOT_INFO = 20
log.basicConfig(level=BOT_INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

TOKEN = "7465141345:AAHkj1SKA-CG9FRGdARz5EbmK_xk2OM9vZA"
DB_LINK = "mongodb://localhost:27017"

client = MongoClient(DB_LINK)
DB = client.get_database("mono-f1")
USER_COLLECTION = DB.get_collection("users")
CARDS_COLLECTION = DB.get_collection("cards")
MARKET_COLLECTION = DB.get_collection("market")
