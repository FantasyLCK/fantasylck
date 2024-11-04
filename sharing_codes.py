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
            "team_value": 0
        }
        print(f"Initialized user data for user ID: {user_id}")

def get_player_value(name):
    data = load_data()  # 데이터 로드
    if name in data["players"]:
        return data["players"][name]["value"]
    else:
        print(f"{name} 선수를 찾을 수 없습니다.")
        return None