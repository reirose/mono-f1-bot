import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.variables import check_cross_marks_colors, translation, roll_types


def generate_settings_keyboard(user: User):
    settings = user.settings
    check_colors = list(check_cross_marks_colors['check'].keys())
    next_check_index = (check_colors.index(settings['check']) + 1) % len(check_colors)
    next_check_color_name = check_colors[next_check_index]

    # Next Cross Color
    cross_colors = list(check_cross_marks_colors['cross'].keys())
    next_cross_index = (cross_colors.index(settings['cross']) + 1) % len(cross_colors)
    next_cross_color_name = cross_colors[next_cross_index]

    # Next Roll Type
    next_roll_type_index = (roll_types.index(settings['roll_type']) + 1) % len(roll_types)
    next_roll_type_name = roll_types[next_roll_type_index]
    keyboard = [
        [InlineKeyboardButton(f"Цвет галочек: "
                              f"{check_cross_marks_colors['check'][settings['check']]}",
                              callback_data=f"settings_set_check_{next_check_color_name}")],
        [InlineKeyboardButton(f"Цвет крестиков: "
                              f"{check_cross_marks_colors['cross'][settings['cross']]}",
                              callback_data=f"settings_set_cross_{next_cross_color_name}")],
        # [InlineKeyboardButton(f"Открытие паков: {translation[settings['roll_type']]}",
        #                       callback_data=f"settings_set_roll_type_{next_roll_type_name}")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def settings_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    resp = "Здесь Вы можете изменить настройки интерфейса:"
    keyboard = generate_settings_keyboard(user)
    await update.effective_user.send_message(resp,
                                             reply_markup=keyboard)


async def change_settings(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    setting_type = re.search("check|cross|roll_type", update.callback_query.data).group(0)
    pattern = f"settings_set_{setting_type}_(.+)"
    settings_new = re.search(pattern, update.callback_query.data).group(1)
    user.settings[setting_type] = settings_new
    user.write()
    keyboard = generate_settings_keyboard(user)
    await update.callback_query.edit_message_reply_markup(reply_markup=keyboard)
    await update.callback_query.answer("Успешно!")
