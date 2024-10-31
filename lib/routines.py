"""
Рутинные функции, не столь относящиеся к игровому процессу, сколь к работе бота
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest, Forbidden

from lib.init import CARDS_COLLECTION, USER_COLLECTION, BOT_INFO, logger
from lib.variables import cards_list, cards_dict, cards_by_category, roll_cards_dict, type_sort_keys

scheduler = BackgroundScheduler()
async_scheduler = AsyncIOScheduler()


def update_free_roll():
    """
    Добавление крутки пользователям
    """
    resp = USER_COLLECTION.update_many({}, {"$inc": {"rolls_available.standard": 1}})
    logger.log(BOT_INFO, f"Updated %i free rolls" % resp.matched_count)


def update_cards():
    """
    Обновление всех необходимых локальных списков и словарей с картами из БД
    """
    db_data = sorted(list(CARDS_COLLECTION.find({}, {"_id": 0})),
                     key=lambda y: (type_sort_keys[y['type']], y['name']))
    for x in db_data:
        cards_dict.update({x["code"]: x})
        if x["type"] not in ["limited", "duo", "team"]:
            cards_list.append(x)
            cards_by_category[x["category"]].append(x["code"])
            roll_cards_dict.update({x["code"]: x})

    logger.log(BOT_INFO, f"Updated {len(db_data)} cards.")


def restart_status_reset():
    resp = USER_COLLECTION.update_many({"status": {"$not": {"$in": ["banned"]}}},
                                       {"$set": {"status": "idle"}})
    logger.log(BOT_INFO, "Status reset successful (%i)" % resp.matched_count)


async def notify_free_pack(*args):
    TOKEN = "7998597879:AAHDOosw1hVVFoEmKz5RuzNymvisTWT5qjg"  # dev-token
    # TOKEN = "7465141345:AAHkj1SKA-CG9FRGdARz5EbmK_xk2OM9vZA"
    bot = Bot(token=TOKEN)
    users = USER_COLLECTION.find({}, {"_id": 0})
    for user in users:
        try:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Открыть",
                                                                   callback_data="pack_open_standard")]])
            await bot.send_message(chat_id=user.get("id"),
                                   text="Привет, тебе выдан бесплатный пак",
                                   reply_markup=keyboard)
        except (BadRequest, Forbidden):
            pass


def clear_logs():
    logger.log(BOT_INFO, "cleared logs successfully")


clear_logs()
restart_status_reset()
