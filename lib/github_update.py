import logging
import os
import subprocess
import sys

import requests


BRANCH = "alpha"
REPO_URL = "https://github.com/reirose/mono-f1-bot.git"
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))


def get_latest_commit_sha():
    api_url = f"https://api.github.com/repos/username/repo/branches/{BRANCH}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()['commit']['sha']
    return None


async def check_updates(update, _):
    current_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=LOCAL_DIR).decode().strip()
    latest_sha = get_latest_commit_sha()

    if latest_sha and current_sha != latest_sha:
        await update.message.reply_text('Обновление...')
        logging.log(25, "Обновление обнаружено, скачивание файлов...")
        subprocess.run(['git', 'fetch', 'origin', BRANCH], cwd=LOCAL_DIR)
        subprocess.run(['git', 'reset', '--hard', f'origin/{BRANCH}'], cwd=LOCAL_DIR)
        await update.message.reply_text('Обновление завершено. Перезабуск бота...')
        logging.log(25, "Скачивание завершено. Перезабуск бота...")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        await update.message.reply_text("Обновлений не обнаружено.")
