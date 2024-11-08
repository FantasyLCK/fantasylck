import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from datetime import datetime, time, timedelta
import pytz
import logging
from sharing_codes import UserData, initialize_user, attendance_data, DAILY_REWARD, ALLOWED_CHANNEL_ID

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_ATTEMPTS_PER_DAY = 2
attempts_data = {}

KST = pytz.timezone("Asia/Seoul")
RESET_HOUR = 6

class Gold(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="육구놀이", description="육구놀이를 실행합니다.")
    async def minigame(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)

            if interaction.channel.id not in ALLOWED_CHANNEL_ID:
                await interaction.followup.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
                return

            user_id = interaction.user.id
            user_data = initialize_user(user_id)  # 사용자 초기화

            now_kst = datetime.now(KST)
            reset_time_kst = datetime.combine(now_kst.date(), time(RESET_HOUR, 0, 0, tzinfo=KST))

            # 지금이 리셋 시간 전이라면 전날로 설정
            if now_kst < reset_time_kst:
                reset_time_kst -= timedelta(days=1)

            # 시도 횟수 초기화
            if user_id not in attempts_data or attempts_data[user_id]['last_reset_time'] < reset_time_kst:
                logger.info(f"Resetting attempts for user {user_id} at {now_kst}. Last reset was at {attempts_data.get(user_id, {}).get('last_reset_time')}")
                attempts_data[user_id] = {'last_reset_time': now_kst, 'attempts': 0}

            # 하루 시도 횟수 초과 체크
            if attempts_data[user_id]['attempts'] >= MAX_ATTEMPTS_PER_DAY:
                await interaction.followup.send("오늘의 시도 횟수를 모두 사용했습니다. **지나친 도박은 정신건강에 해롭습니다.**", ephemeral=True)
                return

            # 사용자 예산 확인
            if user_data.balance < 15:
                await interaction.followup.send("**골드가 부족합니다!**", ephemeral=True)
                return

            # 골드 차감
            user_data.update_balance(-15)

            # 랜덤 숫자 추출
            numbers = random.choices([3, 6, 9], weights=[70, 20, 10], k=3)

            # 출력 메시지
            await interaction.followup.send(f"{numbers[0]}...")
            await asyncio.sleep(1)
            await interaction.followup.send(f"{numbers[1]}...")
            await asyncio.sleep(1)
            await interaction.followup.send(f"{numbers[2]}!!!!!")

            # 획득 골드 계산
            gold_earned = 0
            if numbers == [3, 3, 3]:
                gold_earned = 0
            elif numbers == [3, 6, 9] or numbers == [6, 6, 6]:
                gold_earned = 50
            elif numbers == [9, 9, 9]:
                gold_earned = 100
            elif numbers.count(3) == 2:
                gold_earned = 15
            elif numbers.count(6) == 2:
                gold_earned = 25
            elif numbers.count(9) == 2:
                gold_earned = 35

            # 획득 골드 반영
            user_data.update_balance(gold_earned)
            await interaction.followup.send(f"획득한 골드: {gold_earned}골드. 현재 예산: {user_data.balance}골드.")

            # 시도 횟수 증가
            attempts_data[user_id]['attempts'] += 1
            logger.info(f"User {user_id} has attempted {attempts_data[user_id]['attempts']} times today.")
        except Exception as e:
            logger.error(f"Error in minigame command: {e}")

    @app_commands.command(name="출석", description="출석하고 골드를 받습니다.")
    async def daily_attendance(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)

            if interaction.channel.id not in ALLOWED_CHANNEL_ID:
                await interaction.followup.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
                return

            user_id = interaction.user.id
            user_data = initialize_user(user_id)  # 사용자를 초기화

            # 현재 시간과 출석 기록 확인
            current_time_kst = datetime.now(KST)  # 한국 시간으로 현재 시간 얻기
            today = current_time_kst.date()

            # 마지막 출석 날짜를 확인
            last_attendance = attendance_data.get(user_id)

            # 이미 오늘 출석한 경우 처리
            if last_attendance == today:
                await interaction.followup.send("오늘은 이미 출석했습니다. 내일 다시 출석해주세요!", ephemeral=True)
                return

            # 출석 처리 및 골드 지급
            user_data.daily_login()
            attendance_data[user_id] = today  # 마지막 출석 날짜 기록
            logger.info(f"User {user_id} completed attendance at {current_time_kst}.")
            await interaction.followup.send(f"출석 완료! {DAILY_REWARD} 골드를 받았습니다. 현재 예산: {user_data.balance} 골드", ephemeral=False)
        except Exception as e:
            logger.error(f"Error in attendance command: {e}")

# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(Gold(bot))
