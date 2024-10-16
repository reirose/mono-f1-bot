from collections import namedtuple

BattleData = namedtuple("BattleData",
                        ["battle_id", "player_1", "player_2"])


class Battle:
    def __init__(self, battle_data: BattleData):
        self.battle_id = battle_data.battle_id
        self.player_1 = battle_data.player_1
        self.player_2 = battle_data.player_2
        
