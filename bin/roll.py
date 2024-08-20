import random
from time import time

from telegram import Update
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.keyboard_markup import roll_menu_markup
from lib.variables import cards_list


async def roll_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    telegram_user = update.effective_user
    user = User.get(telegram_user)

    next_free_roll_time = 43200 - (time() - user.last_roll)
    hrs = int(next_free_roll_time // 3600)
    mins = int((next_free_roll_time % 3600) // 60)
    time_left = "меньше минуты" if (not hrs and not mins and not (next_free_roll_time // 60)) \
        else f"{hrs} ч {mins} мин"

    response = (f"<b>Доступно круток:</b> 🏳️‍🌈 {user.rolls_available}\n\n"
                f"До следующей бесплатной попытки: {time_left}")

    await mes.reply_text(response,
                         parse_mode="HTML",
                         reply_markup=roll_menu_markup)


async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    telegram_user = update.effective_user
    user = User.get(telegram_user)

    if not user.rolls_available:
        next_free_roll_time = 43200 - (time() - user.last_roll)
        hrs = int(next_free_roll_time // 3600)
        mins = int((next_free_roll_time % 3600) // 60)
        time_left = "меньше минуты" if (not hrs and not mins and not (next_free_roll_time // 60)) \
            else f"{hrs} ч {mins} мин"

        await mes.reply_text(f"У вас не осталось доступных круток!\n\nОсталось до бесплатной: {time_left}")
        return

    rolled_card = random.choice(list(cards_list.keys()))
    user.rolls_available -= 1
    user.write()

    await mes.reply_text("rolling...")
    j = context.job_queue.run_once(roll_result, 3, data=[user, rolled_card, mes])


async def roll_result(context):
    job = context.job
    user = job.data[0]
    rolled_card = job.data[1]
    mes = job.data[2]

    response = f"Вы получили карту <b>{cards_list[rolled_card]}!</b>"

    if rolled_card in user.collection:
        response += "\n\n<i>Подсказка: повторки можно обменять позже!</i>"

    user.collection.append(rolled_card)
    user.write()

    await mes.reply_text(text=response,
                         reply_markup=roll_menu_markup,
                         parse_mode="HTML")
