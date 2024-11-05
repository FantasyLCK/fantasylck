import discord
from discord.ext import commands
import os
import json

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
def initialize_user(user_id):
    if user_id not in user_data: 
        user_budgets[user_id] = STARTING_BUDGET
        user_data[user_id] = {
            "team": {
                "탑": None,
                "정글": None,
                "미드": None,
                "원딜": None,
                "서폿": None
            },
            "team_value": 0,
        }
        print(f"Initialized user data for user ID: {user_id}")


players_data = {
    "탑": {
        "S": ["도란", "기인"],
        "A": ["제우스", "킹겐"],
        "B": ["퍼펙트", "클리어"],
        "C": ["두두", "미하일"],
        "D": ["프로그", "모건"],
    },
    "정글": {
        "S": ["피넛", "캐니언"],
        "A": ["오너", "루시드"],
        "B": ["표식", "랩터"],
        "C": ["커즈", "실비"],
        "D": ["스폰지", "영재"],
    },
    "미드": {
        "S": ["제카", "쵸비"],
        "A": ["페이커", "쇼메이커"],
        "B": ["비디디", "클로저"],
        "C": ["불독", "피셔"],
        "D": ["예후", "페이트"],
    },
    "원딜": {
        "S": ["바이퍼", "페이즈"],
        "A": ["구마유시", "에이밍"],
        "B": ["데프트", "헤나"],
        "C": ["리퍼", "지우"],
        "D": ["테디", "엔비"],
    },
    "서폿": {
        "S": ["딜라이트", "리헨즈"],
        "A": ["케리아", "켈린"],
        "B": ["베릴", "듀로"],
        "C": ["안딜", "구거"],
        "D": ["플레타", "폴루"]
    }
}

# 선수 데이터 등록
def register_players():
    data = load_data()  # 데이터 로드
    
    for position, tiers in players_data.items():
        for tier, players in tiers.items():
            for name in players:
                # 각 선수의 정보를 데이터에 추가
                if name not in data["players"]:
                    data["players"][name] = {}  # initialize the player data
                data["players"][name].update({
                    "position": position,
                    "tier": tier,
                    "value": TIER_VALUES[tier]  # 티어에 따라 가치 설정
                })

    save_data(data)  # 선수 정보를 파일에 저장


    # 플레이어 가치 가져오기
def get_player_value(name):
    data = load_data()  # 데이터 로드
    if name in data["players"]:
        return data["players"][name]["value"]
    else:
        print(f"{name} 선수를 찾을 수 없습니다.")
        return None
