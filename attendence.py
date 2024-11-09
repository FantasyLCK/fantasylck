import discord
import pytz
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from data import UserData
from sharing_codes import DAILY_REWARD, ALLOWED_CHANNEL_ID


class Attendence(commands.Cog):

    @app_commands.command(name="출석", description="출석하고 골드를 받습니다.")
    async def daily_attendance(self, interaction: discord.Interaction):
        
        if interaction.channel.id not in ALLOWED_CHANNEL_ID:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
            return

        user_id = interaction.user.id
        user_data = UserData.load_from_db(user_id)

        # 현재 시간과 출석 기록 확인
        korea_tz = pytz.timezone('Asia/Seoul')
        current_time_kst = datetime.now(korea_tz)  # 한국 시간으로 현재 시간 얻기
        today = current_time_kst.date()

        # 마지막 출석 날짜 확인
        last_attendance_date = user_data.login_record[-1].date() if user_data.login_record else None


        # 이미 오늘 출석한 경우 처리
        if last_attendance_date == today:
            await interaction.response.send_message("오늘은 이미 출석했습니다. 내일 다시 출석해주세요!", ephemeral=True)
            return

        # 출석 처리 및 골드 지급
        user_data.update_balance(DAILY_REWARD)
        user_data.add_login_record(current_time_kst)
        user_data.save_to_db()  # DB에 업데이트된 정보 저장

        await interaction.response.send_message(f"출석 완료! {DAILY_REWARD} 골드를 받았습니다. 현재 예산: {user_data.balance} 골드", ephemeral=False)


# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(Attendence(bot))
