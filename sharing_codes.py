from fractions import Fraction
import logging

from db_connection import db as _db

logger = logging.getLogger(__name__)

_STARTING_BUDGET = 150

_DAILY_REWARD = 5

# 선수 등록 활성화 플래그
is_registration_active = True
is_sale_active = True

# FT잡담 채널 ID: 1302961629562011750
# FT명령어 채널 ID: 1302944526750453820
# 테섭 채널 ID: 1304615715139223585

_ALLOWED_CHANNEL_ID = [1304615715139223585] # 명령어 채널
_COMMUNITY_CHANEL_ID = [1304615715139223585] # 잡담+명령어 채널

class _BotConfig:

    __default_config = config = _db["game_config"]

    def __init__(self):
        if self.__default_config.find_one() is None:
            self.__default_config.update_one(
                {'id': 0},
                {'$set': {
                    'starting_budget': _STARTING_BUDGET,
                    'daily_reward': _DAILY_REWARD,
                    's_tier_value': 50,
                    'a_tier_value': 40,
                    'b_tier_value': 30,
                    'c_tier_value': 20,
                    'd_tier_value': 10,
                    'single_team_bonus': 10,
                    'pog_bonus': 5,
                    'sale_charge_percentage': 20,
                    'is_registration_active': True,
                    'is_sale_active': True,
                    'allowed_channel_id': [1302944526750453820],
                    'community_channel_id': [1302961629562011750, 1302944526750453820]
                }},
                upsert=True
            )

    def __load_config(self):
        return self.__default_config.find_one({'id': 0})

    @property
    def starting_budget(self) -> int:
        # 초기 예산 설정
        return self.__load_config()['starting_budget']

    @property
    def daily_reward(self) -> int:
        # 출석 골드 설정
        return self.__load_config()['daily_reward']

    @property
    def tier_values(self) -> dict[str, int]:
        # 티어에 따른 가치 정의
        return {
            "S": self.__load_config()['s_tier_value'],
            "A": self.__load_config()['a_tier_value'],
            "B": self.__load_config()['b_tier_value'],
            "C": self.__load_config()['c_tier_value'],
            "D": self.__load_config()['d_tier_value'],
        }

    @property
    def is_registration_active(self) -> bool:
        return self.__load_config()['is_registration_active']

    @is_registration_active.setter
    def is_registration_active(self, new_status: bool):
        self.__default_config.update_one({'id': 0}, {'$set': {'is_registration_active': new_status}})

    @property
    def is_sale_active(self) -> bool:
        return self.__load_config()['is_sale_active']

    @is_sale_active.setter
    def is_sale_active(self, new_status: bool):
        self.__default_config.update_one({'id': 0}, {'$set': {'is_sale_active': new_status}})

    @property
    def allowed_channel_id(self) -> list[int]:
        return self.__load_config()['allowed_channel_id']

    @property
    def community_channel_id(self) -> list[int]:
        return self.__load_config()['community_channel_id']

    @property
    def single_team_bonus(self) -> int:
        return self.__load_config()['single_team_bonus']

    @property
    def pog_bonus(self) -> int:
        return self.__load_config()['pog_bonus']

    @property
    def sale_charge(self) -> Fraction:
        return Fraction(self.__load_config()['sale_charge_percentage'], 100)

_CONFIG = _BotConfig()

def config():
    return _CONFIG
