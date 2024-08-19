import re

from telegram.ext import filters


class FilterIsStatisticButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Статистика", message.text) is not None


statistic_button_filter = FilterIsStatisticButton()
