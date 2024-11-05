from discord.ext import commands
from sharing_codes import user_data, initialize_user, user_budgets, attendance_data, DAILY_REWARD, ALLOWED_CHANNEL_ID
import random
import asyncio
from datetime import datetime, timedelta
import pytz

MAX_ATTEMPTS_PER_DAY = 3
attempts_data = {}

@commands.command()
async def 육구놀이(ctx):

    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return
    
    user_id = ctx.author.id
    user_data = initialize_user(user_id)  # 사용자 초기화

    today = datetime.now().date()

    # 시도 정보 초기화
    if user_id not in attempts_data or attempts_data[user_id]['last_attempt_date'] != today:
        attempts_data[user_id] = {'last_attempt_date': today, 'attempts': 0}

    # 하루 시도 횟수 초과 체크
    if attempts_data[user_id]['attempts'] >= MAX_ATTEMPTS_PER_DAY:
        await ctx.send("오늘의 시도 횟수를 모두 사용했습니다. **지나친 도박은 정신건강에 해롭읍니다.**")
        return
    
    if user_data.balance < 15:  # 사용자 예산 확인
        await ctx.send("**골드가 부족합니다!**")
        return
    
    user_data.update_balance(-15)  # 골드 차감

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
    
    user_data.update_balance(gold_earned)  # 획득 골드 반영
    await ctx.send(f"획득한 골드: {gold_earned}골드. 현재 예산: {user_data.balance}골드.")

    # 시도 횟수 증가
    attempts_data[user_id]['attempts'] += 1

@commands.command()
async def 출석(ctx):
    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return
    
    user_id = ctx.author.id
    user_data = initialize_user(user_id)  # 사용자를 초기화

    # 현재 시간과 출석 기록 확인
    korea_tz = pytz.timezone('Asia/Seoul')
    current_time_kst = datetime.now(korea_tz)  # 한국 시간으로 현재 시간 얻기
    today = current_time_kst.date()

    last_attendance = attendance_data.get(user_id)

    # 출석 시간이 오전 6시 이전인지 확인
    if last_attendance == today and current_time_kst.hour < 6:
        await ctx.send("아직 출석할 수 없습니다! 한국 시간 기준 오전 6시 이후에 출석해 주세요.")
        return

    # 출석 처리 및 골드 지급
    user_data.daily_login()
    attendance_data[user_id] = today  # 마지막 출석 날짜 기록
    await ctx.send(f"출석 완료! {DAILY_REWARD} 골드를 받았습니다. 현재 예산: {user_data.balance} 골드")