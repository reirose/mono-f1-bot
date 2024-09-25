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

category_color: dict = {
    'bronze': '',
    'silver': '️',
    'gold': '',
    'platinum': '',
    'ruby': '💠 ',
    'sapphire': '💠 ',
    'diamond': '💠 '
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

translation: dict = {
    "driver": "Пилот",  # 1
    "duo": "Дуо",  # 2
    "team": "Балтика-тройка",  # 3
    "team_principal": "Руководитель",  # 4
    "track": "Трасса",  # 5
    "car": "Болид",  # 6
    "collab": "Коллаб",  # 7
    "historical": "Историческая",  # 8
    "limited": "Лимитированная",  # 9
    "bronze": "Бронзовая",
    "silver": "Серебряная",
    "gold": "Золотая",
    "platinum": "Платиновая",
    "ruby": "Рубиновая",
    "sapphire": "Сапфировая",
    "diamond": "Алмазная",
    'Alpine': "Alpine",
    'Aston Martin': "Aston Martin",
    'Ferrari': "Ferrari",
    'Haas': "Haas",
    'McLaren': "McLaren",
    'Mercedes': "Mercedes",
    'Red Bull': "Red Bull",
    "RB": "RB",
    "Sauber": "Sauber",
    "Williams": "Williams",
    'MonoF1': "MonoF1",
    '': "Другое"
}

probability_by_category: dict = {
        "silver": 0.30,
        "gold": 0.12,
        "platinum": 0.06,
        "ruby": 0.03,
        "sapphire": 0.015
    }

category_distribution = {
        "bronze": 2,
        "silver": 0,
        "gold": 0,
        "platinum": 0,
        "ruby": 0,
        "sapphire": 0
    }

category_sort_keys: dict[str, int] = {'bronze': 0,
                                      'silver': 1,
                                      'gold': 2,
                                      'platinum': 3,
                                      'ruby': 4,
                                      'sapphire': 5,
                                      'diamond': 6}

team_sort_keys: dict[str, int] = {'Alpine': 0,
                                  'Aston Martin': 1,
                                  'Ferrari': 2,
                                  'Haas': 3,
                                  'McLaren': 4,
                                  'Mercedes': 5,
                                  'Red Bull': 6,
                                  "RB": 7,
                                  "Sauber": 8,
                                  "Williams": 9,
                                  '': 10,
                                  'MonoF1': 10}

type_sort_keys: dict[str, int] = {"driver": 0,
                                  "duo": 1,
                                  "team": 2,
                                  "team_principal": 3,
                                  "track": 4,
                                  "car": 5,
                                  "collab": 6,
                                  "historical": 7,
                                  "limited": 8}

sort_keys_by: dict[str, dict] = {'team': team_sort_keys,
                                 'category': category_sort_keys,
                                 'type': type_sort_keys}

sort_list = ["category", "team", "type"]
sort_list_transl = {'type': 'По типу',
                    'category': 'По редкости',
                    'team': 'По команде'}

cards_in_pack: int = 2

garant_value: int = 10

garant_list: list[str] = ["gold", "platinum", "ruby", "sapphire", "diamond"]

dev_list: list[int] = [352318827, 889865196]
admin_list: list[int] = [352318827, 400977526, 417603391, 522033389, 776014112, 889865196, 1161121344, 1293045951,
                         1306616210, 1949641072, 5163281155, 6983627466]

trades_log_chat_id = -1002401343820
