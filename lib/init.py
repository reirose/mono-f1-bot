"""файл инициализации бота"""

import logging as log

from pymongo import MongoClient

BOT_INFO = 25  # уровень информации для логов, чтобы не выводило лишнюю хуйню
log.basicConfig(level=BOT_INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                filename="log.log")

TOKEN = "7998597879:AAHDOosw1hVVFoEmKz5RuzNymvisTWT5qjg"  # dev-token
# TOKEN = "7465141345:AAHkj1SKA-CG9FRGdARz5EbmK_xk2OM9vZA"
DB_LINK = "mongodb://localhost:27017"

client = MongoClient(DB_LINK)
DB = client.get_database("mono-f1")
USER_COLLECTION = DB.get_collection("users")
CARDS_COLLECTION = DB.get_collection("cards")
MARKET_COLLECTION = DB.get_collection("market")
TRADES_COLLECTION = DB.get_collection("trades")
