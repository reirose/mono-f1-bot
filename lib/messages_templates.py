import json

with open('lib/localization_ru.json', 'r', encoding='utf-8') as f:
    MESSAGE_TEMPLATES = json.load(f)


def get_message_text(template_key, **kwargs):
    """Получает шаблон сообщения и форматирует его с переданными аргументами."""
    template = MESSAGE_TEMPLATES.get(template_key, template_key)
    return template.format(**kwargs)
