import re

from telegram.ext import filters


class FilterStatisticButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Статистика", message.text) is not None


class FilterMenuButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Меню", message.text) is not None


class FilterRollButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Получить карту", message.text) is not None


class FilterRollMenuButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Получение карт", message.text) is not None


statistic_button_filter = FilterStatisticButton()
menu_button_filter = FilterMenuButton()
roll_button_filter = FilterRollButton()
roll_menu_button_filter = FilterRollMenuButton()
