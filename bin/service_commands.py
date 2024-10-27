import json
import os
import re
import subprocess
import sys
import uuid

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from bin.menu import menu
from lib.classes.user import User
from lib.filters import DEV_MODE
from lib.keyboard_markup import main_menu_markup
from lib.init import USER_COLLECTION, CARDS_COLLECTION, PROMO_LINKS_COLLECTION
from lib.variables import cards_dict, roll_cards_dict


async def dev_mode_change(_: Update, __: ContextTypes.DEFAULT_TYPE):
    DEV_MODE.change()


class UpdateError(Exception):
    pass


async def update_user(user: 'User', update_type: str,
                      value: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update_type == "all_cards":
        for code, __ in roll_cards_dict.items():
            if code in user.collection:
                continue
            user.collection.append(code)
        await context.bot.send_message(user.id,
                                       "done")
        user.write()
    elif update_type == "coins":
        user.coins += int(value)
        await context.bot.send_message(user.id,
                                       "<b>Получено</b>:\n"
                                       f"Монеты: {value}",
                                       parse_mode="HTML")
    elif update_type == "rolls":
        if len(value) != 2:
            return
        user.rolls_available[value[0]] += int(value[1])
        await context.bot.send_message(user.id,
                                       "<b>Получено</b>:\n"
                                       f"Крутки: {value}",
                                       parse_mode="HTML")
    elif update_type == "card":
        user.collection.append(value)
        if value not in cards_dict:
            raise UpdateError(f"Неверный код карты: {value}")
        await context.bot.send_message(user.id,
                                       f"<b>Получено</b>:\n"
                                       f"Карта: {cards_dict[value]['name']}",
                                       parse_mode="HTML")
    else:
        raise UpdateError(f"Неверный тип обновления: {update_type}")
    user.write()


async def give_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not len(context.args):
            raise UpdateError("Неверное количество аргументов. Ожидается 3 или более: цель, тип обновления, "
                              "дополнительные значение")

        target, update_type, value = context.args

        if update_type not in ["coins", "rolls", "card", "all_cards"]:
            raise UpdateError(f"Неверный тип обновления: {update_type}")

        if target == "all":
            try:
                ids = [x["id"] for x in USER_COLLECTION.find({})]
            except Exception as e:
                raise UpdateError(f"Ошибка при получении ID пользователей: {str(e)}")

            errors = ""
            for uid in ids:
                try:
                    user = User.get(None, uid)
                    await update_user(user, update_type, value, context)
                except Exception as e:
                    errors += f"Ошибка обновления пользователя {uid}: {str(e)}\n"
            await update.message.reply_text(errors)
            await update.message.reply_text("Пользователи успешно обновлены")
        else:
            try:
                user = User.get(None, int(target))
                await update_user(user, update_type, value, context)
                await update.message.reply_text(f"Пользователь {target} успешно обновлен")
            except ValueError:
                raise UpdateError(f"Неверный ID пользователя: {target}")

    except UpdateError as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"Произошла непредвиденная ошибка: {str(e)}")


async def ribbon_info(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    user = User.get(mes.from_user)
    if not all(code in set(user.collection) for code, __ in roll_cards_dict.items()):
        return

    response = (
        "Лента Коллекционера — это престижный символ признания, венчающий ваш путь истинного собирателя карт. Эта "
        "уникальная награда отмечает ваше неустанное стремление к совершенству и страсть к коллекционированию.\n\n"
        "Как это работает? Жмёте на кнопку, и вуаля:\n"
        "- Вы освободитесь от всех карт, доступных в обычных паках\n"
        "- Взамен вы обретете не только заветную Ленту Коллекционера, но и редчайшую лимитированную карту — настоящее "
        "сокровище для любого коллекционера.\n\n"
        "Погнали?")

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Поехали!", callback_data="ribbon_redeem")]])
    await mes.reply_text(response,
                         reply_markup=reply_markup)


async def unstuck(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    user.status = "idle"
    user.write()
    await menu(update, _)


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    mes = update.message

    User.get(telegram_user, start=True)

    await mes.reply_text(text="Добро пожаловать, снова!",
                         reply_markup=main_menu_markup)

    await menu(update, _)


async def get_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    with open("log.log", "rt") as logfile:
        lines = logfile.readlines()[-int(context.args[0] if context.args else 10):]
        response = ""
        for line in lines:
            response += line

    await mes.reply_text(response)


async def update_github(update, _):
    await update.message.reply_text("Начинаю обновление кода с GitHub...")

    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        if result.returncode == 0:
            await update.message.reply_text("Код успешно обновлен с GitHub. Перезапускаю бота...")
        else:
            await update.message.reply_text(f"Ошибка при обновлении: {result.stderr}")
            return
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")
        return

    try:
        with open('mono-f1.cards.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        CARDS_COLLECTION.delete_many({})
        for doc in data:
            if '_id' in doc and '$oid' in doc['_id']:
                doc['_id'] = doc['_id']['$oid']
        CARDS_COLLECTION.insert_many(data)

        print(f"Обновление базы данных завершено, добавлено {len(data)} записей.")
    except Exception as e:
        print(f"Ошибка при обновлении базы данных: {str(e)}")

    restart_bot()


def restart_bot():
    print("Перезапускаю бота...")
    os.execv(sys.executable, ["py", "main.py"])


async def handle_promo_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    promo_id = re.search("promo_(.+)", context.args[0]).group(1)
    try:
        data = list(PROMO_LINKS_COLLECTION.find({"id": promo_id}))[0]
    except IndexError:
        return
    if data:
        await start(update, context)
        if data.get("activations") == 1:
            PROMO_LINKS_COLLECTION.delete_one({"id": promo_id})
        else:
            PROMO_LINKS_COLLECTION.update_one({"id": promo_id}, {"$inc": {"activations": -1}})
    return


async def generate_promo_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    promo_id = uuid.uuid4().hex
    activations = int(context.args[0])
    PROMO_LINKS_COLLECTION.insert_one({"id": promo_id, "activations": activations})
    await update.effective_chat.send_message(f"Ваша промо-ссылка (х{activations}): "
                                             f"https://t.me/monof1alphabot?start=promo_" + promo_id)


async def cancel_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await menu(update, context)
    return ConversationHandler.END
