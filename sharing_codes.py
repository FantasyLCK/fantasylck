import logging
import os
import json

logger = logging.getLogger(__name__)

# 데이터 파일 경로
DATA_FILE = "players_data.json"

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

user_data = {}

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
        if self.top == None:
            self.__purchase_player(top)
            self.__top = top
        elif top == None:
            self.__sell_player(self.top)
            self.__top = None
        else:
            raise AttributeError

    @property
    def jgl(self):
        return self.__jgl

    @jgl.setter
    def jgl(self, jgl: PlayerData):
        if self.jgl == None:
            self.__purchase_player(jgl)
            self.__jgl = jgl
        elif jgl == None:
            self.__sell_player(self.jgl)
            self.__jgl = None
        else:
            raise AttributeError

    @property
    def mid(self):
        return self.__mid

    @mid.setter
    def mid(self, mid: PlayerData):
        logger.debug(self.__mid)
        if self.__mid == None:
            self.__purchase_player(mid)
            self.__mid = mid
        elif mid == None:
            self.__sell_player(self.mid)
            self.__mid = None
        else:
            raise AttributeError

    @property
    def adc(self):
        return self.__adc

    @adc.setter
    def adc(self, adc: PlayerData):
        if self.adc == None:
            self.__purchase_player(adc)
            self.__adc = adc
        elif adc == None:
            self.__sell_player(self.adc)
            self.__adc = None
        else:
            raise AttributeError

    @property
    def sup(self):
        return self.__sup

    @sup.setter
    def sup(self, sup: PlayerData):
        if self.sup == None:
            self.__purchase_player(sup)
            self.__sup = sup
        elif sup == None:
            self.__sell_player(self.sup)
            self.__sup = None
        else:
            raise AttributeError

    def __purchase_player(self, player: PlayerData):
        if player.value > self.__balance:
            raise ValueError
        self.__balance -= player.value

    def __sell_player(self, player: PlayerData):
        self.__balance += player.value

    def daily_login(self):
        self.__balance += DAILY_REWARD

    def update_balance(self, change: int):
        if change < 0 and abs(change) > self.balance:
            raise ValueError
        self.__balance += change

# 사용자 데이터와 출석 기록을 저장할 딕셔너리
attendance_data = {}

# 선수 등록 활성화 플래그
is_registration_active = True
is_sale_active = True

# FT잡담 채널 ID: 1302961629562011750 
# FT명령어 채널 ID: 1302944526750453820

ALLOWED_CHANNEL_ID = [1302944526750453820, 1301814668154765324] # 명령어 채널
COMMUNITY_CHANEL_ID = [1302961629562011750, 1302944526750453820, 1301814668154765324] # 잡담+명령어 채널

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


# 선수 데이터 등록 및 복구
def register_players():
    data = load_data()  # 데이터 로드

    if "players" not in data:
        data["players"] = {}

    # `players_data`와 비교, 필요한 선수들 등록, 삭제된 선수 복구
    existing_players = set(data["players"].keys())  # 현재 JSON 파일에 있는 선수 목록
    new_players = set(players_data.keys())  # 새로 추가된 선수 목록

    # 삭제된 선수는 복구 (JSON에서 삭제된 선수는 복구)
    for player in existing_players - new_players:
        data["players"][player] = players_data[player]

    # 새로운 선수 추가
    for name, player_info in players_data.items():
        if name not in data["players"]:
            data["players"][name] = {
                "position": player_info["position"],
                "tier": player_info["tier"]
            }

    # 데이터 저장
    save_data(data)
    logger.info("선수 데이터가 성공적으로 등록되었습니다.")
    return data["players"]


# 플레이어 가치 가져오기
def get_player_value(name):
    data = load_data()  # 데이터 로드
    if name in data["players"]:
        return data["players"][name]["value"]
    else:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")
        return None