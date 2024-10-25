import random

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters,\
    CallbackQueryHandler

from lib.classes.user import User

pitstop_jobs_ids: dict = {}
pitstop_kd_list: list = []


def generate_random_word(length: int):
    alphabet = "абвгдежзиклмнопрстуфхцчшщыэюя"
    return "".join(random.choices(alphabet, k=length))


async def pitstop_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in pitstop_kd_list:
        await update.effective_user.send_message("Рано, ёпта, полчаса не прошло ещё")
        return
    await update.effective_chat.send_message("Правила игры: даётся случайный набор из 5 букв, твоя цель — "
                                             "успеть повторить этот набор. Не успеешь — следующая попытка "
                                             "через 30 минут!\n\nГотов?",
                                             reply_markup=InlineKeyboardMarkup([[
                                                 InlineKeyboardButton("Готов!",
                                                                      callback_data="pitstop_start")]]))


async def pitstop_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in pitstop_kd_list:
        await update.effective_user.send_message("Рано, ёпта, полчаса не прошло ещё")
        return ConversationHandler.END

    resp = generate_random_word(5)
    timer = 3
    await update.callback_query.edit_message_text(f"У тебя 3 секунды!\nТвоё слово:\n\n{resp}",
                                                  reply_markup=None)
    job = context.job_queue.run_once(pitstop_fail, when=timer, data=[update])
    pitstop_jobs_ids.update({update.effective_user.id: {"text": resp,
                                                        "job": job}})
    return "pitstop_parse_input"


async def pitstop_parse_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in pitstop_kd_list:
        return pitstop_conv_handler.END

    user = User.get(update.effective_user)
    if update.message.text.lower() != pitstop_jobs_ids.get(user.id)["text"]:
        await update.effective_user.send_message("Увы, не пробил!(\n\n"
                                                 "<i>Следующая попытка - через 30 минут</i>",
                                                 parse_mode="HTML")
        pitstop_jobs_ids.get(user.id)["job"].remove()
        context.job_queue.run_once(reset_user, when=60 * 30, data=[update.effective_user.id])
        pitstop_kd_list.append(update.effective_user.id)
        return pitstop_conv_handler.END

    await update.effective_user.send_message("Харош успел, ма-ла-ца!\nДержи 5 🪙!\n\n"
                                             "<i>Следующая попытка - через 30 минут</i>",
                                             parse_mode="HTML")
    user.coins += 5
    user.write()
    pitstop_jobs_ids.get(update.effective_user.id).get('job').job.remove()
    pitstop_jobs_ids.pop(update.effective_user.id)
    context.job_queue.run_once(reset_user, when=60 * 30, data=[update.effective_user.id])
    pitstop_kd_list.append(update.effective_user.id)
    return pitstop_conv_handler.END


async def pitstop_fail(context):
    resp = ("Упс, не успел. Колесо проколото, штаны спущены, сзади злой Хорни идёт ругать тебя за проигранную гонку🤥"
            "\n\n<i>Следующая попытка - через 30 минут</i>")
    update = context.job.data[0]
    await update.effective_user.send_message(resp, parse_mode="HTML")
    pitstop_jobs_ids.pop(update.effective_user.id)
    context.job_queue.run_once(reset_user, when=60 * 30, data=[update.effective_user.id])
    pitstop_kd_list.append(update.effective_user.id)
    return pitstop_conv_handler.END


def reset_user(context):
    user_id = context.job.data[0]
    pitstop_kd_list.remove(user_id)


pitstop_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(pitstop_start, pattern="pitstop_start")],
    states={
        "pitstop_parse_input": [MessageHandler(filters.TEXT & ~filters.COMMAND, pitstop_parse_input)],
    },
    fallbacks=[]
)
