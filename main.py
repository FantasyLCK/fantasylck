import discord
from discord.ext import commands
from player_database import DATA_FILE
import json
import os
from team_management import 선수등록, 선수판매
from convenience import 내팀보기, 선수목록, 명령어, 관리자
from gold import 육구놀이, 출석
from admin import 선수추가, 선수삭제, 선수수정, on, off

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

# 봇의 프리픽스 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 봇이 준비되었을 때 실행되는 이벤트
@bot.event
async def on_ready():
    print(f'봇이 실행되었습니다: {bot.user}')

# 전체 사용자의 예산을 담는 딕셔너리
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

# 사용자의 팀과 예산 데이터를 저장할 딕셔너리
user_data = {}


# 사용자 데이터와 출석 기록을 저장할 딕셔너리
attendance_data = {}

# 선수 등록 활성화 플래그
is_registration_active = True
is_sale_active = True


# 봇 설정
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)


# 명령어 등록
bot.add_command(선수등록)
bot.add_command(선수판매)

bot.add_command(내팀보기)
bot.add_command(선수목록)
bot.add_command(명령어)
bot.add_command(관리자)

bot.add_command(육구놀이)
bot.add_command(출석)

bot.add_command(선수추가)
bot.add_command(선수수정)
bot.add_command(선수삭제)
bot.add_command(on)
bot.add_command(off)


# Bot 실행
TOKEN = 'YOUR_BOT_TOKEN'
bot.run(TOKEN)


# 메인 함수
bot.run("MTMwMTQ0NTMwNzg5MTk3NDE4NQ.GZUs2V.C5bdfdnqve6B2rEPLymHt6LdTyiRWXaT5-S7os")
