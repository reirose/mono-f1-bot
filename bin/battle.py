import math
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, filters, MessageHandler, CommandHandler, \
    CallbackQueryHandler

from lib.classes.user import User
from lib.keyboard_markup import CARDS_PER_PAGE, other_menu_markup
from lib.messages_templates import get_message_text
from lib.variables import cards_dict


async def generate_collection_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    user = User.get(update.effective_user)
    user_cards = user.collection
    user_cards = [cards_dict[x] for x in user_cards]

    unique_cards = list(set(card['code'] for card in user_cards))
    unique_cards.sort()

    total_pages = math.ceil(len(unique_cards) / CARDS_PER_PAGE)

    if not unique_cards:
        await context.bot.send_message(text="У вас нет карточек. Чтобы получить их "
                                            "- перейдите в раздел Получение карт.",
                                       chat_id=update.effective_chat.id,
                                       reply_markup=other_menu_markup)
        return

    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    current_page_cards = unique_cards[start:end]

    keyboard = []
    for card_code in current_page_cards:
        card = next(card for card in user_cards if card['code'] == card_code)
        button_text = f"{card['name']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"battle_select_{card['code']}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("<<", callback_data=f"battle_page_0"))
        nav_buttons.append(InlineKeyboardButton("<", callback_data=f"battle_page_{page - 1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page + 1}", callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(">", callback_data=f"battle_page_{page + 1}"))
        nav_buttons.append(InlineKeyboardButton(">>", callback_data=f"battle_page_{total_pages - 1}"))

    keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="battle_init_close")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


async def battle_init_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    user = User.get(update.effective_user)

    if user.battle_bet:
        return

    response = get_message_text("battle_choose_card")
    reply_markup = await generate_collection_keyboard(update, context, page=kwargs.get("page", 0))
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
        return

    await update.effective_chat.send_message(response,
                                             reply_markup=reply_markup)


async def battle_confirm_choice(update: Update, context: ContextTypes):
    card_code = re.search("c_\\d{3}", update.callback_query.data).group(0)
    user = User.get(update.effective_user)
    page = context.user_data.get("battle_choice_page", 0)

    if card_code not in user.collection:
        await update.callback_query.answer("Карты нет в коллекции!")
        await update.callback_query.delete_message()
        await battle_init_menu(update, context, page=page)
        return

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Да",
                                                               callback_data=f"battle_choice_confirm_{card_code}")],
                                         [InlineKeyboardButton("Отмена",
                                                               callback_data=f"battle_choice_cancel_{page}")]])

    await update.callback_query.edit_message_text(get_message_text("battle_confirm_choice",
                                                                   card_name=cards_dict.get(card_code)),
                                                  reply_markup=reply_markup)


async def battle_init_game(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    if user.battle_bet:
        await update.effective_chat.send_message("У вас есть незаконченная игра! "
                                                 "Если вы хотите отозвать предложение - нажмите "
                                                 "/battle_cancel", parse_mode="HTML")
        return ConversationHandler.END

    card_code = re.search("c_\\d{3}", update.callback_query.data).group(0)
    user.battle_bet = card_code
    # user.collection.remove(card_code)
    user.write()

    await update.effective_chat.send_message("Введите имя или ID пользователя, с которым хотите сыграть")
    return "battle_parse_id"


async def battle_parse_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    user = User.get(update.effective_user)
    try:
        receiver_id = int(mes.text)
    except ValueError:
        receiver_id = mes.text

    if receiver_id == mes.from_user.id or receiver_id == mes.from_user.username:
        await update.effective_chat.send_message("Неверный ввод")
        return "battle_parse_id"

    receiver = User.get(user=None, update=receiver_id)
    if not receiver:
        await update.effective_chat.send_message(get_message_text("user_not_found"))
        return "battle_parse_id"

    if not receiver.collection:
        await update.effective_chat.send_message(get_message_text("opponent_no_cards_in_collection"))
        return "battle_parse_id"

    if receiver.battle_bet:
        await update.effective_chat.send_message("Пользователь уже в игре! Попробуйте сыграть с кем-то другим!")
        return "battle_parse_id"

    rec_accept_callback = f"battle_invite_accept_{user.id}_{user.battle_bet}"
    rec_decline_callback = f"battle_invite_decline_{user.id}"
    rec_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Принять", callback_data=rec_accept_callback)],
                                         [InlineKeyboardButton("Отклонить", callback_data=rec_decline_callback)]])

    sent = await context.bot.send_message(chat_id=receiver.id,
                                          text=get_message_text("battle_invite_received",
                                                                username=update.effective_user.username),
                                          reply_markup=rec_keyboard)

    user_cancel_callback = f"battle_invite_cancel_{receiver.id}_{sent.message_id}"
    user_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Отменить приглашение",
                                                                callback_data=user_cancel_callback)]])

    await update.effective_chat.send_message(text=get_message_text("battle_invite_sent",
                                                                   username=receiver.username),
                                             reply_markup=user_keyboard)

    return ConversationHandler.END


async def battle_cancel(update, _):
    await update.effective_user.send_message(get_message_text("battle_cancelled_by_user"))
    return ConversationHandler.END


battle_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(battle_init_game, pattern=r'battle_choice_confirm_c_\d{3}')],
    states={
        "battle_parse_id": [MessageHandler(filters.TEXT & ~filters.COMMAND, battle_parse_id)],
    },
    fallbacks=[CommandHandler("battle_cancel", battle_cancel)]
)
