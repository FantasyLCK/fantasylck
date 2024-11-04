import discord
from discord.ext import commands
from player_database import add_player, update_player, delete_player
import json
import os
import random
import asyncio
from datetime import datetime, timedelta


# 데이터 파일 경로
DATA_FILE = "player_data.json"

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

# 사용자 육구놀이 사용 기록 저장 딕셔너리
user_game_data = {}

# 사용자 데이터와 출석 기록을 저장할 딕셔너리
attendance_data = {}

# 선수 등록 활성화 플래그
is_registration_active = True
is_sale_active = True

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

# 선수 데이터 초기화
def initialize_players():
    data = load_data()
    if "players" not in data:
        data["players"] = {}
        save_data(data)
    return data["players"]

# 선수 데이터 등록
def register_players():
    data = load_data()  # 데이터 로드
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

    for position, tiers in players_data.items():
        for tier, players in tiers.items():
            for name in players:
                # 각 선수의 정보를 데이터에 추가
                data["players"][name] = {
                    "position": position,
                    "tier": tier,
                    "value": TIER_VALUES[tier]  # 티어에 따라 가치 설정
                }

    save_data(data)  # 선수 정보를 파일에 저장

# 초기 선수 등록
register_players()

# 플레이어 가치 가져오기
def get_player_value(name):
    data = load_data()  # 데이터 로드
    if name in data["players"]:
        return data["players"][name]["value"]
    else:
        print(f"{name} 선수를 찾을 수 없습니다.")
        return None

# 선수 등록 명령어
@bot.command()
async def 선수등록(ctx, position, name):
    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자를 초기화

    if not is_registration_active:
        await ctx.send("선수 등록이 비활성화되어 있습니다.")
        return

    # 선수 정보 확인
    try:
        players_data = load_data()["players"]  # 선수 데이터 로드
        player_info = next(({"name": name, "tier": players["tier"]} for player, players in players_data.items() 
                            if player == name), None)

        if player_info is None:
            await ctx.send("올바른 선수 이름과 포지션을 입력하세요.")
            return

        player_value = get_player_value(name)

        # 예산 확인
        if player_value is None:
            await ctx.send("선수의 가치를 확인할 수 없습니다.")
            return

        if user_budgets[user_id] < player_value:
            await ctx.send(f"**예산이 부족합니다.** 현재 예산: {user_budgets[user_id]} 골드")
            return

        # 이미 등록된 포지션에 선수가 있으면 판매 후 등록
        if user_data[user_id]["team"][position] is not None:
            existing_player = user_data[user_id]["team"][position]
            user_budgets[user_id] += existing_player["value"]
            user_data[user_id]["team_value"] -= existing_player["value"]

        # 선수 등록
        user_data[user_id]["team"][position] = {"name": name, "value": player_value}
        user_budgets[user_id] -= player_value
        user_data[user_id]["team_value"] += player_value

        await ctx.send(f"{position}에 {name} 선수를 등록했습니다. 남은 예산: {user_budgets[user_id]} 골드")

    except KeyError as e:
        await ctx.send("선수 데이터를 로드하는 데 문제가 발생했습니다.")
        print(f"KeyError 발생: {e}")
    except Exception as e:
        await ctx.send("오류가 발생했습니다.")
        print(f"오류 발생: {e}")

# 선수 판매 명령어
@bot.command()
async def 선수판매(ctx, position=None):
    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자 초기화

    if not is_sale_active:
        await ctx.send("선수 판매가 비활성화되어 있습니다.")
        return

    if position == "all":
        total_value = 0
        for pos, player in user_data[user_id]["team"].items():
            if player:
                total_value += player["value"]
                user_data[user_id]["team"][pos] = None
        user_budgets[user_id] += total_value
        await ctx.send(f"모든 선수가 판매되었으며 {total_value} 골드가 반환되었습니다.")
    else:
        if position not in user_data[user_id]["team"] or user_data[user_id]["team"][position] is None:
            await ctx.send(f"{position} 포지션에 선수가 없습니다.")
            return
        name = user_data[user_id]["team"][position]["name"]
        # 선수의 현재 가치를 가져와서 업데이트
        player_value = get_player_value(name)  # 가치를 업데이트
        user_data[user_id]["team"][position] = None  # 포지션의 선수를 삭제
        user_budgets[user_id] += player_value
        await ctx.send(f"{position} 포지션의 {name} 선수가 판매되어 {player_value} 골드가 반환되었습니다.")


# 내팀 명령어
@bot.command()
async def 내팀(ctx):
    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자 초기화 추가

    team = user_data[user_id]["team"]
    budget = user_budgets[user_id]

    # 팀 가치 계산
    team_value = 0
    for pos, info in team.items():
        if info:
            # 선수의 현재 티어를 가져와서 가치를 업데이트
            player_value = get_player_value(info["name"])  # 가치를 업데이트
            info["value"] = player_value  # 선수 데이터에 가치를 업데이트
            team_value += player_value

    team_info = "\n".join([f"{pos}: {info['name']} (가치: {info['value']} 골드)" if info else f"{pos}: 없음" for pos, info in team.items()])
    await ctx.send(f"현재 팀:\n{team_info}\n\n예산: {user_budgets[user_id]} 골드\n팀 가치: {team_value} 골드")

# 선수 목록 명령어
@bot.command()
async def 선수목록(ctx, position: str):
    # 선수 데이터 로드
    players_data = load_data()["players"]

    # 포지션에 해당하는 선수들을 티어별로 정리
    tiered_players = {}
    for name, data in players_data.items():
        if data["position"].lower() == position.lower():
            tier = data["tier"]
            if tier not in tiered_players:
                tiered_players[tier] = []
            tiered_players[tier].append(name)

    # 포지션에 선수가 없는 경우 처리
    if not tiered_players:
        await ctx.send(f"{position} 포지션에 해당하는 선수가 없습니다.")
        return

    # 티어별로 정렬하여 출력 형식 준비
    output = f"**{position} 포지션 선수 목록:**\n"
    for tier, players in sorted(tiered_players.items(), key=lambda x: TIER_VALUES[x[0]], reverse=True):
        players_list = ", ".join(players)
        gold_value = TIER_VALUES[tier]
        output += f"{tier} ({gold_value}골드) | {players_list}\n"

    await ctx.send(output)


@bot.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def 선수추가(ctx, name: str, position: str, tier: str):
    add_player(name, position, tier)
    await ctx.send(f"{name} 선수가 추가되었습니다.")

@bot.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def 선수수정(ctx, name: str, position: str = None, tier: str = None):
    update_player(name, position, tier)
    await ctx.send(f"{name} 선수 정보가 수정되었습니다.")

@bot.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def 선수삭제(ctx, name: str):
    delete_player(name)
    await ctx.send(f"{name} 선수가 삭제되었습니다.")

@bot.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def on(ctx):
    global is_registration_active, is_sale_active
    is_registration_active = True
    is_sale_active = True
    await ctx.send("선수 등록 및 판매가 활성화되었습니다.")

@bot.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def off(ctx):
    global is_registration_active, is_sale_active
    is_registration_active = False
    is_sale_active = False
    await ctx.send("선수 등록 및 판매가 비활성화되었습니다.")

# 사용자 골드 관리
def update_user_gold(user_id, amount, add_play_count=True):
    data = load_user_data()
    if str(user_id) not in data:
        data[str(user_id)] = {"gold": 150, "play_count": 0}  # 초기값 설정

    user_data = data[str(user_id)]

    if add_play_count and user_data["play_count"] < 5:  # 하루에 5번 제한
        user_data["gold"] += amount
        user_data["play_count"] += 1
    elif not add_play_count:  # 획득한 골드를 추가할 때는 play_count를 증가시키지 않음
        user_data["gold"] += amount
    else:
        return False  # 기회 초과

    save_user_data(data)
    return True

# 게임 관련 설정
GAME_COST = 15  # 육구놀이 비용
GAME_LIMIT = 5  # 24시간 당 게임 횟수 제한
PROBABILITIES = [3] * 90 + [6] * 8 + [9] * 2 # 확률에 따른 숫자 배열 (3은 90%, 6은 8.5%, 9는 1.5%)
last_played = {}  # 사용자의 마지막 플레이 기록
game_counts = {}  # 사용자의 하루 당 플레이 횟수 기록



# 육구놀이 명령어
@bot.command()
async def 육구놀이(ctx):
    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자 초기화
    
    if user_budgets[user_id] < 15:  # 사용자 예산 확인
        await ctx.send("**골드가 부족합니다!**")
        return
    
    user_budgets[user_id] -= 15  # 골드 차감

    numbers = random.choices([3, 6, 9], weights=[70, 20, 10], k=3)
    
    # 출력 메세지
    await ctx.send(f"{numbers[0]}...")
    await asyncio.sleep(1)  # 1초 대기
    await ctx.send(f"{numbers[1]}...")
    await asyncio.sleep(1)  # 1초 대기
    await ctx.send(f"{numbers[2]}!!!!!")
    
    # 획득 골드 계산
    gold_earned = 0
    if numbers == [3, 3, 3]:
        gold_earned = 0
    elif numbers == [3, 6, 9]:
        gold_earned = 50
    elif numbers == [6, 6, 6]:
        gold_earned = 50
    elif numbers == [9, 9, 9]:
        gold_earned = 100
    elif numbers.count(3) == 2:
        gold_earned = 15
    elif numbers.count(6) == 2:
        gold_earned = 25
    elif numbers.count(9) == 2:
        gold_earned = 35
    
    user_budgets[user_id] += gold_earned  # 획득 골드 반영
    await ctx.send(f"획득한 골드: {gold_earned}골드. 현재 예산: {user_budgets[user_id]}골드.")

# 출석 명령어
@bot.command()
async def 출석(ctx):
    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자를 초기화

    # 현재 날짜와 출석 기록 확인
    today = datetime.now().date()
    last_attendance = attendance_data.get(user_id)

    if last_attendance == today:
        await ctx.send("이미 오늘 출석하셨습니다! 내일 다시 시도해 주세요.")
        return

    # 출석 처리 및 골드 지급
    user_budgets[user_id] += DAILY_REWARD
    attendance_data[user_id] = today  # 마지막 출석 날짜 기록
    await ctx.send(f"출석 완료! {DAILY_REWARD} 골드를 받았습니다. 현재 예산: {user_budgets[user_id]} 골드")


# 사용자 명령어 목록
@bot.command()
async def 명령어(ctx):
    commands_list = """
    **사용 가능한 명령어:**
    **!선수등록 [포지션] [선수명]**: 지정된 포지션에 선수를 등록합니다. ex) !선수등록 미드 페이커
    **!선수판매 [포지션]**: 지정된 포지션의 선수를 판매합니다. 'all'을 입력하면 모든 선수가 판매됩니다. ex) !선수판매 미드
    **!선수목록 [포지션]**: 해당 포지션의 선수 목록과 가치를 확인합니다. ex) !선수목록 미드
    **!내팀**: 현재 등록된 팀과 예산을 확인합니다.
    **!육구놀이**: 15골드를 지불하고 간단한 미니게임을 진행합니다. '!육구놀이룰'을 통해 규칙을 확인 할 수 있어요!
    **!출석**: 하루에 한 번 출석하여 5골드를 수령합니다.

    만든이: 롤소남 (www.instagram.com/lolsonam80)
    """
    await ctx.send(commands_list)

# 관리자 명령어 목록
@bot.command()
async def 관리자명령어(ctx):
    manager_commands_list = """
    **관리자 전용 명령어:**
    **!선수추가 [이름] [포지션] [티어]**
    **!선수수정 [이름] [포지션] [티어]**
    **!선수삭제 [이름]**
    **!on**: 이적시장 활성화
    **!off**: 이적시장 비활성화
    **이이이잉 쇼메이쿠**
    """
    await ctx.send(manager_commands_list)

# 육구놀이 규칙
@bot.command()
async def 육구놀이룰(ctx):
    gamerule = """
    게임 한판 당 15골드
    
    3,3,3 = 0골드 획득
    6,6,6 = 50골드 획득
    9,9,9 = 100골드 획득
    
    3,3,X = 15골드 획득
    6,6,X = 25골드 획득
    9,9,X = 35골드 획득
    
    3,6,9 = 50골드 획득 (단, 순서대로)

    **지나친 도박은 정신건강에 해롭읍니다.**
    """
    await ctx.send(gamerule)

# 메인 함수
bot.run("MTMwMTQ0NTMwNzg5MTk3NDE4NQ.GZUs2V.C5bdfdnqve6B2rEPLymHt6LdTyiRWXaT5-S7os")
