import logging

import discord
from discord.ext import commands
import os
import json

logger = logging.getLogger(__name__)

# 데이터 파일 경로
DATA_FILE = "player_data.json"

user_data = {}
user_budgets = {}

# 초기 예산 설정
STARTING_BUDGET = 150

# 출석 골드 설정
DAILY_REWARD = 5

# 티어에 따른 가치 정의
TIER_VALUES = {
    "S": 50,
    "A": 40,
    "B": 30,
    "C": 20,
    "D": 10,
}

class PlayerData:
    __name:str
    __tier:str

    def __init__(self, name:str, tier:str):
        self.__name = name
        self.__tier = tier

    @property
    def name(self):
        return self.__name

    @property
    def value(self) -> int:
        return TIER_VALUES[self.__tier]

    @property
    def tier(self):
        return self.__tier

    @tier.setter
    def tier(self, tier: str):
        if tier not in TIER_VALUES:
            raise ValueError
        self.__tier = tier

class UserData:
    __id = int
    __top: PlayerData = None
    __jgl: PlayerData = None
    __mid: PlayerData = None
    __adc: PlayerData = None
    __sup: PlayerData = None
    __balance: int

    def __init__(self, id):
        self.__id = id
        self.__balance = STARTING_BUDGET

    @property
    def id(self):
        return self.__id

    @property
    def team_data(self):
        return {"탑": self.__top, "정글": self.__jgl, "미드": self.__mid, "원딜": self.__adc, "서폿": self.__sup}

    @property
    def team_value(self) -> int:
        value_sum = 0
        for pos in self.team_data:
            if self.team_data[pos] != None:
                value_sum += self.team_data[pos].value
        return value_sum

    @property
    def balance(self):
        return self.__balance

    @property
    def top(self):
        return self.__top

    @top.setter
    def top(self, top: PlayerData):
        if self.top != None:
            self.__update_balance(top)
            self.__top = top
        else:
            raise AttributeError

    @property
    def jgl(self):
        return self.__jgl

    @jgl.setter
    def jgl(self, jgl: PlayerData):
        if self.jgl != None:
            self.__update_balance(jgl)
            self.__jgl = jgl
        else:
            raise AttributeError

    @property
    def mid(self):
        return self.__mid

    @mid.setter
    def mid(self, mid: PlayerData):
        if self.mid != None:
            self.__update_balance(mid)
            self.__mid = mid
        else:
            raise AttributeError

    @property
    def adc(self):
        return self.__adc

    @adc.setter
    def adc(self, adc: PlayerData):
        if self.adc != None:
            self.__update_balance(adc)
            self.__adc = adc
        else:
            raise AttributeError

    @property
    def sup(self):
        return self.__sup

    @sup.setter
    def sup(self, sup: PlayerData):
        if self.sup != None:
            self.__update_balance(sup)
            self.__sup = sup
        else:
            raise AttributeError

    def __update_balance(self, player: PlayerData):
        if player.value > self.__balance:
            raise ValueError
        self.__balance -= player.value

# 사용자 데이터와 출석 기록을 저장할 딕셔너리
attendance_data = {}

# 선수 등록 활성화 플래그
is_registration_active = True
is_sale_active = True

# 런칭 채널 id: 1302944526750453820

ALLOWED_CHANNEL_ID = [1301814668154765324, 1301709446786973737]
COMMUNITY_CHANEL_ID = [1302961629562011750, 1301814668154765324, 1301709446786973737]

# 사용자 데이터 로드
def load_user_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# 사용자 데이터 저장
def save_user_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# JSON 파일이 존재하지 않는 경우 빈 데이터 생성
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"players": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# 데이터를 JSON 파일로 저장
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# 공유된 함수
def initialize_user(user_id) -> UserData:
    if user_id not in user_data:
        user_data[user_id] = UserData(user_id)
        logger.info(f"Initialized user data for user ID: {user_id}")
    else:
        logger.debug(f"User data for user ID: {user_id} already initialized")
    return user_data[user_id]

players_data = {
    "도란": {"position": "탑", "tier": "S"},
    "기인": {"position": "탑", "tier": "S"},
    "제우스": {"position": "탑", "tier": "A"},
    "킹겐": {"position": "탑", "tier": "A"},
    "퍼펙트": {"position": "탑", "tier": "B"},
    "클리어": {"position": "탑", "tier": "B"},
    "두두": {"position": "탑", "tier": "C"},
    "미하일": {"position": "탑", "tier": "C"},
    "프로그": {"position": "탑", "tier": "D"},
    "모건": {"position": "탑", "tier": "D"},
    
    "피넛": {"position": "정글", "tier": "S"},
    "캐니언": {"position": "정글", "tier": "S"},
    "오너": {"position": "정글", "tier": "A"},
    "루시드": {"position": "정글", "tier": "A"},
    "표식": {"position": "정글", "tier": "B"},
    "랩터": {"position": "정글", "tier": "B"},
    "커즈": {"position": "정글", "tier": "C"},
    "실비": {"position": "정글", "tier": "C"},
    "스폰지": {"position": "정글", "tier": "D"},
    "영재": {"position": "정글", "tier": "D"},
    
    "제카": {"position": "미드", "tier": "S"},
    "쵸비": {"position": "미드", "tier": "S"},
    "페이커": {"position": "미드", "tier": "A"},
    "쇼메이커": {"position": "미드", "tier": "A"},
    "비디디": {"position": "미드", "tier": "B"},
    "클로저": {"position": "미드", "tier": "B"},
    "불독": {"position": "미드", "tier": "C"},
    "피셔": {"position": "미드", "tier": "C"},
    "예후": {"position": "미드", "tier": "D"},
    "페이트": {"position": "미드", "tier": "D"},
    
    "바이퍼": {"position": "원딜", "tier": "S"},
    "페이즈": {"position": "원딜", "tier": "S"},
    "구마유시": {"position": "원딜", "tier": "A"},
    "에이밍": {"position": "원딜", "tier": "A"},
    "데프트": {"position": "원딜", "tier": "B"},
    "헤나": {"position": "원딜", "tier": "B"},
    "리퍼": {"position": "원딜", "tier": "C"},
    "지우": {"position": "원딜", "tier": "C"},
    "테디": {"position": "원딜", "tier": "D"},
    "엔비": {"position": "원딜", "tier": "D"},
    
    "딜라이트": {"position": "서폿", "tier": "S"},
    "리헨즈": {"position": "서폿", "tier": "S"},
    "케리아": {"position": "서폿", "tier": "A"},
    "켈린": {"position": "서폿", "tier": "A"},
    "베릴": {"position": "서폿", "tier": "B"},
    "듀로": {"position": "서폿", "tier": "B"},
    "안딜": {"position": "서폿", "tier": "C"},
    "구거": {"position": "서폿", "tier": "C"},
    "플레타": {"position": "서폿", "tier": "D"},
    "폴루": {"position": "서폿", "tier": "D"},
}


# 선수 데이터 등록
def register_players():
    data = load_data()  # 데이터 로드

    if "players" not in data:
        data["players"] = {}

    # 기존의 players_data 구조를 기반으로 데이터 등록
    for position, tiers in players_data.items():
        for tier, player_names in tiers.items():
            for name in player_names:
                # 중복 방지
                if name not in data["players"]:
                    data["position"][position] = {
                        'tier'[tier]: ['name'[name]]
                    }

    save_data(data)
    return data["players"]



# 플레이어 가치 가져오기
def get_player_value(name):
    data = load_data()  # 데이터 로드
    if name in data["players"]:
        return data["players"][name]["value"]
    else:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")
        return None