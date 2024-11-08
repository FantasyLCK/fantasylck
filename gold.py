import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from datetime import datetime, time, timedelta
import pytz
from sharing_codes import UserData, initialize_user, attendance_data, DAILY_REWARD, ALLOWED_CHANNEL_ID


class MiniGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="육구놀이", description="육구놀이를 실행합니다.")
    async def minigame(self, interaction: discord.Interaction):
        if interaction.channel.id not in ALLOWED_CHANNEL_ID:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=False)
            return

        user_id = interaction.user.id
        user_data = initialize_user(user_id)  # 사용자 초기화


        if user_data.balance < 15:  # 사용자 예산 확인
            await interaction.response.send_message("**골드가 부족합니다!**", ephemeral=True)
            return

        user_data.update_balance(-15)  # 골드 차감

        numbers = random.choices([3, 6, 9], weights=[70, 20, 10], k=3)

        # 출력 메시지
        await interaction.response.send_message(f"{numbers[0]}...")
        await asyncio.sleep(1)  # 1초 대기
        await interaction.followup.send(f"{numbers[1]}...")
        await asyncio.sleep(1)  # 1초 대기
        await interaction.followup.send(f"{numbers[2]}!!!!!")

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
        await interaction.followup.send(f"획득한 골드: {gold_earned}골드. 현재 예산: {user_data.balance}골드.")
        

    @app_commands.command(name="출석", description="출석하고 골드를 받습니다.")
    async def daily_attendance(self, interaction: discord.Interaction):
        if interaction.channel.id not in ALLOWED_CHANNEL_ID:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
            return

        user_id = interaction.user.id
        user_data = initialize_user(user_id)  # 사용자를 초기화

        # 현재 시간과 출석 기록 확인
        korea_tz = pytz.timezone('Asia/Seoul')
        current_time_kst = datetime.now(korea_tz)  # 한국 시간으로 현재 시간 얻기
        today = current_time_kst.date()

        # 마지막 출석 날짜를 확인
        last_attendance = attendance_data.get(user_id)

        # 이미 오늘 출석한 경우 처리
        if last_attendance == today:
            await interaction.response.send_message("오늘은 이미 출석했습니다. 내일 다시 출석해주세요!", ephemeral=True)
            return

        # 출석 시간이 오전 6시 이전인 경우, 출석 제한
        if current_time_kst.hour < 6:
            await interaction.response.send_message("아직 출석할 수 없습니다! 한국 시간 기준 오전 6시 이후에 출석해 주세요.", ephemeral=True)
            return

        # 출석 처리 및 골드 지급
        user_data.daily_login()
        attendance_data[user_id] = today  # 마지막 출석 날짜 기록
        await interaction.response.send_message(f"출석 완료! {DAILY_REWARD} 골드를 받았습니다. 현재 예산: {user_data.balance} 골드", ephemeral=False)

# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(MiniGames(bot))
