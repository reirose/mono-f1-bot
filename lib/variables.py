import datetime

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
    "standard": 10,
    "pack_gold": 30,
    "gem": 50
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
    "champion": "Чемпион",
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
    "": "Другое",
    "standard": "Стандартный",
    "pack_gold": "Золотой",
    "gem": "Драгоценный",
    "new_message": "Стандартное",
    "edit_message": "Компактное",
    "one_message": "Быстрое"
}

probability_by_category: dict = {
    "silver": .12,
    "gold": .06,
    "platinum": .025,
    "ruby": .01,
    "sapphire": .0065
}

cumulative_probability_by_category: dict = {
    "standard": {
        "sapphire": .0065,
        "ruby": .0165,
        "platinum": .0665,
        "gold": .1665,
        "silver": .2915
    },
    "pack_gold": {
        "platinum": .15,
        "gold": .45,
    },
    "gem": {
        "sapphire": .1,
        "ruby": .2,
        "platinum": .3,
    }
}

category_distribution = {
    "standard": {
        "bronze": 2,
        "silver": 0,
        "gold": 0,
        "platinum": 0,
        "ruby": 0,
        "sapphire": 0
    },
    "pack_gold": {
        "bronze": 1,
        "silver": 1,
        "gold": 0,
        "platinum": 0
    },
    "gem": {
        "bronze": 1,
        "silver": 1,
        "gold": 1,
        "platinum": 0,
        "ruby": 0,
        "sapphire": 0
    }
}

MAX_CARDS_IN_PACK: dict[str, int] = {
    "standard": 3,
    "pack_gold": 3,
    "gem": 4
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
                                  "limited": 7}

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

dev_list: list[int] = [352318827, 889865196, 6720093285]
admin_list: list[int] = [352318827, 400977526, 417603391, 522033389, 776014112, 889865196, 1161121344, 1293045951,
                         1306616210, 1949641072, 5163281155, 6983627466, 7581615486]

trades_log_chat_id = -1002401343820

achievements_sort_order = {
    "collector_bronze": 0,
    "collector_silver": 1,
    "collector_gold": 2,
    "packs_opener_bronze": 3,
    "packs_opener_silver": 4,
    "packs_opener_gold": 5,
    "trader_bronze": 6,
    "trader_silver": 7,
    "trader_gold": 8,
    "spender": 9,
    "oldschool": 10,
    "rockefeller": 11
}

achievements_dict = {
    "collector_bronze":
        {"name": "Собрал 🤏 чу-чуть 🤏 совсем", "requirement": lambda user: len(user.collection) >= 10,
         "desc": "За сбор 10 карт в коллекции"},
    "collector_silver":
        {"name": "Солидный склад", "requirement": lambda user: len(user.collection) >= 50,
         "desc": "За сбор 50 карт в коллекции"},
    "collector_gold":
        {"name": "Типа коллекционер", "requirement": lambda user: len(user.collection) >= 100,
         "desc": "За сбор 100 карт в коллекции"},
    "packs_opener_bronze":
        {"name": "Начинающий вскрыватель паков", "requirement": lambda user: user.statistics["packs_opened"] >= 10,
         "desc": "За открытие 10 паков"},
    "packs_opener_silver":
        {"name": "Знаток картонок", "requirement": lambda user: user.statistics["packs_opened"] >= 50,
         "desc": "За открытие 50 паков"},
    "packs_opener_gold":
        {"name": "Паковый император", "requirement": lambda user: user.statistics["packs_opened"] >= 100,
         "desc": "За открытие 100 паков"},
    "trader_bronze":
        {"name": "Мелкий барыга", "requirement": lambda user: user.statistics["trades_complete"] >= 5,
         "desc": "5 завершённых обменов"},
    "trader_silver":
        {"name": "Опытный перекупщик", "requirement": lambda user: user.statistics["trades_complete"] >= 20,
         "desc": "20 завершённых обменов"},
    "trader_gold":
        {"name": "Торговый магнат", "requirement": lambda user: user.statistics["trades_complete"] >= 50,
         "desc": "50 завершённых обменов"},
    "spender":
        {"name": "Куда деньги дел?", "requirement": lambda user: user.statistics["coins_spent"] >= 1000,
         "desc": "Потрачено 1000 монет. Оно того стоило?"},
    "rockefeller":
        {"name": "Рокфеллер", "requirement": lambda user: user.coins >= 10000,
         "desc": "Накопил 10000 монет. А зачем, можно вопрос?"},
    "oldschool":
        {"name": "Старожил",
         "requirement": lambda user:
         (int((datetime.datetime.now().timestamp() - user.date_of_registration) // 86400) + 1) >= 30,
         "desc": "30 дней в игре. Неплохо для новичка"}
}

cards_pics_cache = {}

pitstop_difficulty_parameters = {
    "easy": {
        "length": 5,
        "time": 5,
        "reward": 5
    },
    "normal": {
        "length": 7,
        "time": 5,
        "reward": 10
    },
    "hard": {
        "length": 7,
        "time": 3,
        "reward": 15
    },
}

check_cross_marks_colors = {
    "check": {"grey": "☑️",
              "green": "✅",
              "none": ""},
    "cross": {"none": "",
              "red": "❌",
              "grey": "✖️"}
}

roll_types = ["new_message", "edit_message", "one_message"]
