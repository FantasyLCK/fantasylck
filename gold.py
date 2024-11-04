from discord.ext import commands
from sharing_codes import user_data, initialize_user, user_budgets, attendance_data, DAILY_REWARD, ALLOWED_CHANNEL_ID
import random
import asyncio
from datetime import datetime, timedelta

MAX_ATTEMPTS_PER_DAY = 3
attempts_data = {}

@commands.command()
async def 육구놀이(ctx):

    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return
    
    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자 초기화

    today = datetime.now().date()

    # 시도 정보 초기화
    if user_id not in attempts_data or attempts_data[user_id]['last_attempt_date'] != today:
        attempts_data[user_id] = {'last_attempt_date': today, 'attempts': 0}

    # 하루 시도 횟수 초과 체크
    if attempts_data[user_id]['attempts'] >= MAX_ATTEMPTS_PER_DAY:
        await ctx.send("오늘의 시도 횟수를 모두 사용했습니다. 내일 다시 시도해 주세요.")
        return
    
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

@commands.command()
async def 출석(ctx):

    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return
    
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
