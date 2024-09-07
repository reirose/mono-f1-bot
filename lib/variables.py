cards_list: list = []
cards_dict: dict = {}
cards_by_category: dict = {
    "common": [],
    "uncommon": [],
    "rare": [],
    "epic": [],
    "legendary": []
}

category_to_plain_text: dict = {
    "common": "Обычная",
    "uncommon": "Необычная",
    "rare": "Редкая",
    "epic": "Эпическая",
    "legendary": "Легендарная"
}

category_prices: dict = {
    "common": 1,
    "uncommon": 4,
    "rare": 12,
    "epic": 24,
    "legendary": 50
}

packs_prices: dict = {
    1: 10,
    2: 20,
    3: 28,
    5: 47,
    10: 90
}

type_to_plain_text: dict = {
    "driver": "Пилот",
    "duo": "Дуо",
    "team": "Команда",
    "team_principal": "Руководитель",
    "track": "Трасса",
    "car": "Болид",
    "event": "Ивент",
    "unique": "Уникальная",
    "exclusive": "Эксклюзивная"
}

probability_by_category: dict = {
    "uncommon": {
        1: 0.30,
        2: 0.15
    },
    "rare": {
        1: 0.12
    },
    # "epic": {
    #     1: 0.01
    # },
    # "legendary": {
    #     1: 0.01
    # }
}

cards_in_pack: int = 5


dev_list: list = [352318827]
