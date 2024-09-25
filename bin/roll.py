import datetime
import logging
import random

from telegram import Update
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.init import BOT_INFO
from lib.keyboard_markup import roll_menu_markup
from lib.variables import probability_by_category, cards_by_category, translation, garant_list, \
    roll_cards_dict, category_sort_keys, garant_value, category_distribution


# def select_card_weighted(garant: bool = None, user: User = None):
#     categories = ["bronze"] * cards_in_pack
#
#     for category, probabilities in probability_by_category.items():
#         rand = random.random()
#         slots_for_category = 0
#         for nof, prob in probabilities.items():
#             if rand < prob:
#                 slots_for_category = nof
#
#         if slots_for_category > 0:
#             available_indices = [i for i in range(cards_in_pack) if categories[i] == "bronze"]
#             chosen_indices = available_indices[:slots_for_category]
#             for index in chosen_indices:
#                 categories[index] = category
#
#     if not any(cat in ["gold", "ruby", 'sapphire', 'platinum'] for cat in categories) and garant:
#         logging.log(BOT_INFO, "garant rolled")
#         categories[categories.index("bronze")] = random.choices(["gold", "platinum", "ruby", "sapphire"],
#                                                                 [.42, .27, .17, .16])[0]
#
#     rolled_cards = []
#     for cat in categories:
#         card = roll_cards_dict[random.choice(cards_by_category[cat])]
#         while card in rolled_cards or card["code"] in user.last_roll:
#             card = roll_cards_dict[random.choice(cards_by_category[cat])]
#         rolled_cards.append(card)
#
#     user.last_roll = [x["code"] for x in rolled_cards]
#     user.write()
#     return rolled_cards


def select_card_weighted(garant: bool = None, user: User = None):
    categories = []
    for category, count in category_distribution.items():
        for _ in range(count):
            categories.append(category)

    for category, prob in probability_by_category.items():
        if random.random() < prob:
            categories.append(category)

    if not any(cat in ["gold", "ruby", 'sapphire', 'platinum'] for cat in categories) and garant:
        logging.log(BOT_INFO, "garant rolled")
        categories.append(random.choices(["gold", "platinum", "ruby", "sapphire"], [.42, .27, .17, .16])[0])

    rolled_cards = []
    for cat in categories:
        card = roll_cards_dict[random.choice(cards_by_category[cat])]
        while card in rolled_cards or card["code"] in user.last_roll:
            card = roll_cards_dict[random.choice(cards_by_category[cat])]
        rolled_cards.append(card)

    user.last_roll = [x["code"] for x in rolled_cards]
    user.write()
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

    response = (f"<b>Доступно круток:</b> 🏳️‍🌈 {user.rolls_available}\n"
                f"Гарант: {user.garant}\n\n"
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
        nextday = (now.hour > 8 and now.hour >= 20) or (now.hour < 8)
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

    garant = user.garant >= garant_value
    rolled_cards = sorted(select_card_weighted(garant=garant, user=user),
                          key=lambda x: category_sort_keys.get(x['category'], float('inf')))

    logging.log(BOT_INFO, (f"{user.username} rolled: "
                           f"{', '.join([card['name'] for card in rolled_cards])}"))

    user.garant = 0 if (garant or any(card in garant_list for card in [x["category"] for x in rolled_cards])) else \
        user.garant + 1
    user.rolls_available -= 1
    user.status = 'rolling'
    user.statistics["packs_opened"] += 1
    user.write()

    ROLL_DELAY = 1
    context.job_queue.run_once(roll_pre_result, ROLL_DELAY, data=[user, rolled_cards, mes])
    await update.message.reply_text(text="крутим-вертим")


async def roll_pre_result(context):
    job = context.job
    user = job.data[0]
    rolled_cards = job.data[1]
    mes = job.data[2]

    response = f"Получены карты: \n\n"

    for card in rolled_cards:
        response += (f"{translation[card['category']]} "
                     f"<b>{card['name']}!</b> "
                     f"{'🆕 ' if card['code'] not in user.collection else ''}\n")

        user.collection.append(card["code"])

    await mes.reply_text(text=response,
                         reply_markup=roll_menu_markup,
                         parse_mode="HTML")

    user.status = "idle"
    user.write()
