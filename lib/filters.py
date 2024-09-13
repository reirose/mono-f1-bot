"""
Фильтры для хендлеров текстовых кнопок
суть - в проверке выполнения условий, прописанных в filter(self, message)
если true - бот выполняет команду, если нет - то не выполняет :)
самое главное - после создания класса фильтра создать его объект (пример в конце) и в хендлерах использовать уже объект
"""

import logging
import re

from telegram.ext import filters

from lib.variables import dev_list

DEV_MODE = False  # режим разработки - пользование возможно только пользователям с id в dev_list
if DEV_MODE:
    logging.critical("DEBUG MODE")


class DevMode(filters.MessageFilter):
    def filter(self, message) -> bool:
        if DEV_MODE:
            return message.from_user.id in dev_list
        else:
            return True


class FilterOtherButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Другое", message.text) is not None


class FilterMenuButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Меню", message.text) is not None


class FilterRollButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Получить карту", message.text) is not None


class FilterRollMenuButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Получение карт", message.text) is not None


class FilterCollectionMenuButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Коллекция", message.text) is not None


class FilterCollectionListButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Список карт", message.text) is not None


class FilterShowCardButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Посмотреть карту", message.text) is not None


class FilterShopButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Магазин", message.text) is not None


class FilterMeButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Обо мне", message.text) is not None


class FilterMarketButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Маркет", message.text) is not None


other_button_filter = FilterOtherButton()
menu_button_filter = FilterMenuButton()
roll_button_filter = FilterRollButton()
roll_menu_button_filter = FilterRollMenuButton()
collection_menu_button_filter = FilterCollectionMenuButton()
collection_list_button_filter = FilterCollectionListButton()
show_card_button_filter = FilterShowCardButton()
shop_button_filter = FilterShopButton()
me_button_filter = FilterMeButton()
market_button_filter = FilterMarketButton()
dev_mode = DevMode()
