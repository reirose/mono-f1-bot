"""
Фильтры для хендлеров текстовых кнопок
суть - в проверке выполнения условий, прописанных в filter(self, message)
если true - бот выполняет команду, если нет - то не выполняет :)
самое главное - после создания класса фильтра создать его объект (пример в конце) и в хендлерах использовать уже объект
"""

import logging
import re

from telegram import Message
from telegram.ext import filters

from lib.classes.user import User
from lib.variables import dev_list, admin_list


class DevMode:
    def __init__(self):
        self.dev_mode = True

    def change(self):
        self.dev_mode = not self.dev_mode
        logging.critical("DEV MODE IS " + ("ON" if self.dev_mode else "OFF"))


DEV_MODE = DevMode()


class DevMode(filters.MessageFilter):
    def filter(self, message) -> bool:
        if DEV_MODE.dev_mode and message.chat.type == "private":
            return message.from_user.id in dev_list
        else:
            return True


class IsAdminFilter(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.from_user.id in admin_list


class FilterOtherButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Другое", message.text) is not None


class FilterMenuButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Меню", message.text) is not None


class FilterRollButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Открыть пак", message.text) is not None


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


class FilterPacksShopButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Паки", message.text) is not None


class FilterShopButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Магазин", message.text) is not None


class FilterMeButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Обо мне", message.text) is not None


class FilterMarketButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Маркет", message.text) is not None


class FilterTradeButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Отправить", message.text) is not None


class FilterAllCardsButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Все карты", message.text) is not None


class FilterCoinflipMenuButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("Монетка", message.text) is not None


class FilterCoinflipButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("С игроком", message.text) is not None


class FilterCoinflipPVEButton(filters.MessageFilter):
    def filter(self, message) -> bool:
        return message.text is not None and re.search("С ботом", message.text) is not None


class FilterUserNotBanned(filters.MessageFilter):
    def filter(self, message: Message) -> bool:
        try:
            return User.get(message.from_user).status != "banned"
        except AttributeError:
            return True


class FilterAnonTradeButton(filters.MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.text is not None and re.search("Трейды", message.text) is not None


class FilterMyOffersButton(filters.MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.text is not None and re.search("Мои предложения", message.text) is not None


class FilterOffersButton(filters.MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.text is not None and re.search("Предложения игроков", message.text) is not None


class FilterBattleButton(filters.MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.text is not None and re.search("Битва картами", message.text) is not None


not_banned_filter = FilterUserNotBanned()
anon_trade_button_filter = FilterAnonTradeButton()
other_button_filter = FilterOtherButton()
menu_button_filter = FilterMenuButton()
roll_button_filter = FilterRollButton()
roll_menu_button_filter = FilterRollMenuButton()
collection_menu_button_filter = FilterCollectionMenuButton()
collection_list_button_filter = FilterCollectionListButton()
show_card_button_filter = FilterShowCardButton()
packs_shop_button_filter = FilterPacksShopButton()
shop_button_filter = FilterShopButton()
me_button_filter = FilterMeButton()
market_button_filter = FilterMarketButton()
trade_button_filter = FilterTradeButton()
all_cards_button_filter = FilterAllCardsButton()
coinflip_menu_button_filter = FilterCoinflipMenuButton()
coinflip_button_filter = FilterCoinflipButton()
coinflip_pve_button_filter = FilterCoinflipPVEButton()
my_offers_button_filter = FilterMyOffersButton()
offers_button_filter = FilterOffersButton()
battle_init_button_filter = FilterBattleButton()

is_admin = IsAdminFilter()
dev_mode = DevMode()
