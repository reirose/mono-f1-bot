cards_list: list = []
cards_dict: dict = {}
roll_cards_dict: dict = {}
cards_by_category: dict = {
    "bronze": [],
    "silver": [],
    "gold": [],
    "platinum": [],
    "ruby": [],
    "sapphire": [],
    "diamond": []
}

category_to_plain_text: dict = {
    "bronze": "Бронзовая",
    "silver": "Серебряная",
    "gold": "Золотая",
    "platinum": "Платиновая",
    "ruby": "Рубиновая",
    "sapphire": "Сапфировая",
    "diamond": "Алмазная"
}

category_prices: dict = {
    "bronze": 1,
    "silver": 4,
    "gold": 8,
    "platinum": 16,
    "ruby": 26,
    "sapphire": 38,
    "diamond": 50
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
    "team": "Балтика-тройка",
    "team_principal": "Руководитель",
    "track": "Трасса",
    "car": "Болид",
    "collab": "Коллаб",
    "historical": "Историческая",
    "limited": "Лимитированная"
}

probability_by_category: dict = {
    "silver": {
        1: 0.30
    },
    "gold": {
        1: 0.15
    },
    "platinum": {
        1: 0.075
    },
    # "ruby": {
    #     1: 0.0375
    # },
    # "sapphire": {
    #     1: 0.01875
    # },
    "diamond": {
        1: 0.009375
    }
}

category_sort_keys: dict = {'bronze': 0,
                            'silver': 1,
                            'gold': 2,
                            'platinum': 3,
                            'ruby': 4,
                            'sapphire': 5,
                            'diamond': 6}

cards_in_pack: int = 3

garant_list: list = ["gold", "platinum", "ruby", "sapphire", "diamond"]

dev_list: list = [352318827, 889865196]
