from telegram import ReplyKeyboardMarkup, KeyboardButton


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def get_collection_list(user_collection: list) -> list:
    return [KeyboardButton(x) for x in user_collection] + [KeyboardButton("Меню")] if user_collection \
        else [KeyboardButton("Меню")]


main_menu_buttons = [KeyboardButton("🏳️‍🌈 Получение карт"), KeyboardButton("🏳️‍🌈 Статистика"),
                     KeyboardButton("🏳️‍🌈 Коллекция")]

roll_menu_buttons = [KeyboardButton("🏳️‍🌈 Получить карту"), KeyboardButton("🏳️‍🌈 Меню")]

main_menu_markup = ReplyKeyboardMarkup(build_menu(main_menu_buttons, n_cols=2), resize_keyboard=True)
roll_menu_markup = ReplyKeyboardMarkup(build_menu(roll_menu_buttons, n_cols=2), resize_keyboard=True)
