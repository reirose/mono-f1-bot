import logging
import re

from telegram.ext import filters


DEV_MODE = 0
if DEV_MODE:
    logging.critical("DEBUG MODE")


class DevMode(filters.MessageFilter):
    def filter(self, message):
        if DEV_MODE:
            return message.from_user.id == 352318827
        else:
            return True


class FilterOtherButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Другое", message.text) is not None


class FilterMenuButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Меню", message.text) is not None


class FilterRollButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Получить карту", message.text) is not None


class FilterRollMenuButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Получение карт", message.text) is not None


class FilterCollectionMenuButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Коллекция", message.text) is not None


class FilterCollectionListButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Список карт", message.text) is not None


class FilterShowCardButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Посмотреть карту", message.text) is not None


class FilterShopButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Магазин", message.text) is not None


class FilterMeButton(filters.MessageFilter):
    def filter(self, message):
        return message.text is not None and re.search("Обо мне", message.text) is not None


class FilterMarketButton(filters.MessageFilter):
    def filter(self, message):
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
