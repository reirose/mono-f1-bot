import random

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, \
    CallbackQueryHandler

from lib.classes.user import User
from lib.variables import pitstop_difficulty_parameters

pitstop_jobs_ids: dict = {}
pitstop_kd_list: list = []


def generate_random_word(length: int):
    alphabet = "абвгдежзиклмнопрстуфхцчшщыэюя"
    return "".join(random.choices(alphabet, k=length))


async def pitstop_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in pitstop_kd_list:
        await update.effective_user.send_message("Слишком рано, полчаса еще не прошло")
        return
    await update.effective_chat.send_message("Правила игры: даётся случайный набор из 5 букв, ваша цель — "
                                             "успеть повторить этот набор. Не успеете — следующая попытка "
                                             "через 30 минут!\n\nВыбирайте сложность игры и мы приступаем!",
                                             reply_markup=InlineKeyboardMarkup([[
                                                 InlineKeyboardButton("Легко",
                                                                      callback_data="pitstop_start_easy")],
                                                 [InlineKeyboardButton("Нормально",
                                                                       callback_data="pitstop_start_normal")],
                                                 [InlineKeyboardButton("Сложно",
                                                                       callback_data="pitstop_start_hard")]
                                             ]))


async def pitstop_start(update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in pitstop_kd_list:
        await update.effective_user.send_message("Слишком рано, полчаса еще не прошло")
        return ConversationHandler.END
    diff = update.callback_query.data.split("_")[-1]
    data = pitstop_difficulty_parameters[diff]
    length = data['length']
    time = data['time']
    resp = generate_random_word(length)
    timer = time
    await update.callback_query.edit_message_text(f"У тебя {time} сек.!\nТвоё слово:\n\n{resp}",
                                                  reply_markup=None)
    job = context.job_queue.run_once(pitstop_fail, when=timer, data=[update])
    pitstop_jobs_ids.update({update.effective_user.id: {"text": resp,
                                                        "job": job
                                                        }})
    context.user_data["reward"] = data.get("reward")
    return "pitstop_parse_input"


async def pitstop_parse_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in pitstop_kd_list:
        return pitstop_conv_handler.END

    user = User.get(update.effective_user)
    if update.message.text.lower() != pitstop_jobs_ids.get(user.id)["text"]:
        await update.effective_user.send_message("Увы, неправильно!(\n\n"
                                                 "<i>Следующая попытка - через 30 минут</i>",
                                                 parse_mode="HTML")
        pitstop_jobs_ids.get(user.id)["job"].remove()
        context.job_queue.run_once(reset_user, when=60 * 30, data=[update.effective_user.id])
        pitstop_kd_list.append(update.effective_user.id)
        return pitstop_conv_handler.END
    reward = context.user_data["reward"]

    await update.effective_user.send_message(f"Поздравляю, вы успели!\nПолучено: {reward} 🪙.\n\n"
                                             "<i>Следующая попытка - через 30 минут</i>",
                                             parse_mode="HTML")
    user.coins += reward
    user.write()
    pitstop_jobs_ids.get(update.effective_user.id).get('job').job.remove()
    pitstop_jobs_ids.pop(update.effective_user.id)
    context.job_queue.run_once(reset_user, when=60 * 30, data=[update.effective_user.id])
    pitstop_kd_list.append(update.effective_user.id)
    return pitstop_conv_handler.END


async def pitstop_fail(context):
    resp = ("Увы, но время закончилось!"
            "\n\n<i>Следующая попытка - через 30 минут</i>")
    update = context.job.data[0]
    await update.effective_user.send_message(resp, parse_mode="HTML")
    pitstop_jobs_ids.pop(update.effective_user.id)
    context.job_queue.run_once(reset_user, when=60 * 30, data=[update.effective_user.id])
    pitstop_kd_list.append(update.effective_user.id)
    return pitstop_conv_handler.END


async def reset_user(context):
    user_id = context.job.data[0]
    pitstop_kd_list.remove(user_id)


pitstop_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(pitstop_start, pattern="pitstop_start_(.+)")],
    states={
        "pitstop_parse_input": [MessageHandler(filters.TEXT & ~filters.COMMAND, pitstop_parse_input)],
    },
    fallbacks=[],
    allow_reentry=True
)
