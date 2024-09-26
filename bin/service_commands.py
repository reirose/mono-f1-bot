from telegram import Update
from telegram.ext import ContextTypes

from bin.menu import menu
from lib.classes.user import User
from lib.filters import DEV_MODE
from lib.keyboard_markup import main_menu_markup
from lib.init import USER_COLLECTION
from lib.variables import cards_dict


async def dev_mode_change(_: Update, __: ContextTypes.DEFAULT_TYPE):
    DEV_MODE.change()


class UpdateError(Exception):
    pass


async def update_user(user: 'User', update_type: str,
                      value: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update_type == "coins":
        user.coins += int(value)
        await context.bot.send_message(user.id,
                                       "<b>Получено</b>:\n"
                                       f"Монеты: {value}",
                                       parse_mode="HTML")
    elif update_type == "rolls":
        user.rolls_available += int(value)
        await context.bot.send_message(user.id,
                                       "<b>Получено</b>:\n"
                                       f"Крутки: {value}",
                                       parse_mode="HTML")
    elif update_type == "card":
        user.collection.append(value)
        await context.bot.send_message(user.id,
                                       f"<b>Получено</b>:\n"
                                       f"Карта: {cards_dict[value]['name']}",
                                       parse_mode="HTML")
    else:
        raise UpdateError(f"Неверный тип обновления: {update_type}")
    user.write()


async def give_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if len(context.args) != 3:
            raise UpdateError("Неверное количество аргументов. Ожидается 3: цель, тип обновления, значение")

        target, update_type, value = context.args

        if update_type not in ["coins", "rolls", "card"]:
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


async def unstuck(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    user.status = "idle"
    user.write()
    await menu(update, _)


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    mes = update.message

    User.get(telegram_user)

    await mes.reply_text(text="Добро пожаловать, снова!",
                         reply_markup=main_menu_markup)

    await menu(update, _)
