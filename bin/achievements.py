from telegram import Update
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.variables import achievements_dict


def check_achievements(user: User) :
    """
    Проверяет достижения пользователя и возвращает список выполненных достижений.
    """
    completed_achievements = []

    for achievement_id, achievement in achievements_dict.items():
        if achievement["requirement"](user):
            completed_achievements.append(achievement_id)

    return completed_achievements


def update_user_achievements(user: User):
    """
    Обновляет достижения пользователя и возвращает список новых достижений.
    """

    current_achievements = set(check_achievements(user))
    new_achievements = current_achievements - set(user.achievements)

    user.achievements = list(current_achievements)

    return list(new_achievements)


async def bot_check_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    new_achievements = update_user_achievements(user)
    for ach in new_achievements:
        await context.bot.send_message(text=f"Получено достижение: <i>{achievements_dict[ach]['name']}</i>",
                                       chat_id=user.id,
                                       parse_mode="HTML")
    user.achievements += new_achievements
    user.write()
