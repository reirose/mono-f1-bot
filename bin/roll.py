import datetime
import logging
import random

from telegram import Update
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.keyboard_markup import roll_menu_markup
from lib.variables import probability_by_category, cards_by_category, cards_in_pack, cards_dict, category_to_plain_text


def select_card_weighted():
    # LEGENDARY_N
    # EPIC_N
    categories = ["common"] * cards_in_pack

    for category, probabilities in probability_by_category.items():
        slots_for_category = 0
        for nof, prob in probabilities.items():
            rand = random.random()
            if rand < prob:
                slots_for_category = nof

        if slots_for_category > 0:
            available_indices = [i for i in range(cards_in_pack) if categories[i] == "common"]
            chosen_indices = available_indices[:slots_for_category]
            for index in chosen_indices:
                categories[index] = category

    rolled_cards = []
    for cat in categories:
        card = cards_dict[random.choice(cards_by_category[cat])]
        if card in rolled_cards:
            card = cards_dict[random.choice(cards_by_category[cat])]
        rolled_cards.append(card)
    return rolled_cards


async def roll_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    telegram_user = update.effective_user
    user = User.get(telegram_user)

    now = datetime.datetime.now()
    nextday = True if (now.hour > 8 and now.hour >= 20) or (now.hour < 8) else False
    next_free_roll_time = datetime.datetime(hour=8 if nextday else 20,
                                            minute=0,
                                            second=0,
                                            year=now.year,
                                            month=now.month,
                                            day=now.day) - now
    hrs = int(next_free_roll_time.seconds // 3600)
    mins = int((next_free_roll_time.seconds % 3600) // 60)
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

    if user.status == 'rolling':
        await mes.reply_text(text="Вы уже получаете карту, подождите!")
        return

    if not user.rolls_available or user.rolls_available <= 0:
        now = datetime.datetime.now()
        nextday = True if (now.hour > 8 and now.hour >= 20) or (now.hour < 8) else False
        next_free_roll_time = datetime.datetime(hour=8 if nextday else 20,
                                                minute=0,
                                                second=0,
                                                year=now.year,
                                                month=now.month,
                                                day=now.day) - now
        hrs = int(next_free_roll_time.seconds // 3600)
        mins = int((next_free_roll_time.seconds % 3600) // 60)
        time_left = "меньше минуты" if (not hrs and not mins and not (next_free_roll_time // 60)) \
            else f"{hrs} ч {mins} мин"

        await mes.reply_text(f"У вас не осталось доступных круток!\n\nОсталось до бесплатной: {time_left}")
        return

    rolled_cards = select_card_weighted()
    print(f"{user.username} rolled: "
          f"{', '.join([card['name'] for card in rolled_cards])}")
    user.rolls_available -= 1
    user.status = 'rolling'
    user.write()

    ROLL_DELAY = 1
    context.job_queue.run_once(roll_pre_result, ROLL_DELAY, data=[user, rolled_cards, mes])
    await update.message.reply_text(text="крутим-вертим")


async def roll_pre_result(context):
    job = context.job
    user = job.data[0]
    rolled_cards = job.data[1]
    mes = job.data[2]

    response = (f"Получена карта: {category_to_plain_text[rolled_cards[0]['category']]} "
                f"<b>{rolled_cards[0]['name']}!</b> "
                f"{'🆕 ' if rolled_cards[0]['code'] not in user.collection else ''}\n")

    user.collection.append(rolled_cards[0]["code"])
    user.write()
    rolled_cards.pop(0)

    sent = await mes.reply_text(text=response,
                                reply_markup=roll_menu_markup,
                                parse_mode="HTML")
    context.job_queue.run_once(update_roll_result, 1, data=[user, rolled_cards, mes, sent])


async def update_roll_result(context):
    job = context.job
    user = job.data[0]
    rolled_cards = job.data[1]
    mes = job.data[2]
    sent = job.data[3]

    if not rolled_cards:
        user.status = "idle"
        user.write()
        return

    response = (f"Получена карта: {category_to_plain_text[rolled_cards[0]['category']]} "
                f"<b>{rolled_cards[0]['name']}!</b> "
                f"{'🆕 ' if rolled_cards[0]['code'] not in user.collection else ''}\n")

    user.collection.append(rolled_cards[0]["code"])
    user.write()
    rolled_cards.pop(0)
    await mes.reply_text(text=response,
                         reply_markup=roll_menu_markup,
                         parse_mode="HTML")
    context.job_queue.run_once(update_roll_result, 1, data=[user, rolled_cards, mes, sent])
