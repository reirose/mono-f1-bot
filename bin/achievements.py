from random import randint

from telegram import Update
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.variables import achievements_dict


def check_achievements(user: User):
    """
    Проверяет достижения пользователя и возвращает список выполненных достижений.
    """
    completed_achievements = []

    for achievement_id, achievement in achievements_dict.items():
        if achievement["requirement"](user) and achievement_id not in user.achievements:
            completed_achievements.append(achievement_id)

    return completed_achievements


def update_user_achievements(user: User):
    """
    Обновляет достижения пользователя и возвращает список новых достижений.
    """

    new_achievements = set(check_achievements(user))

    return list(new_achievements)


async def bot_check_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    user = kwargs['user'] if 'user' in kwargs else User.get(update.effective_user)
    new_achievements = update_user_achievements(user)
    for ach in new_achievements:
        await context.bot.send_message(text=f"Получено достижение: <i>{achievements_dict[ach]['name']}</i>",
                                       chat_id=user.id,
                                       parse_mode="HTML")
        user.coins += randint(10, 20)
    user.achievements += new_achievements
    user.write()
