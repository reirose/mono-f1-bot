"""файл инициализации бота"""
from pymongo import MongoClient

import logging
from logging.handlers import RotatingFileHandler

BOT_INFO = 25  # уровень информации для логов, чтобы не выводило лишнюю хуйню

# Настройки логгирования
log_file = 'log.log'
max_log_size = 1024 * 1024  # 1 KB
backup_count = 5  # Количество резервных копий логов

# Создание обработчика для ротации логов
rotating_handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=backup_count)
rotating_handler.setLevel(BOT_INFO)

# Форматирование логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rotating_handler.setFormatter(formatter)

# Создание логгера и добавление обработчика
logger = logging.getLogger('bot')
logger.setLevel(BOT_INFO)
logger.addHandler(rotating_handler)


# TOKEN = "7998597879:AAHDOosw1hVVFoEmKz5RuzNymvisTWT5qjg"  # dev-token
TOKEN = "7465141345:AAHkj1SKA-CG9FRGdARz5EbmK_xk2OM9vZA"
DB_LINK = "mongodb://localhost:27017"

client = MongoClient(DB_LINK)
DB = client.get_database("mono-f1")
USER_COLLECTION = DB.get_collection("users")
CARDS_COLLECTION = DB.get_collection("cards")
MARKET_COLLECTION = DB.get_collection("market")
# BATTLES_COLLECTION = DB.get_collection("battles")
