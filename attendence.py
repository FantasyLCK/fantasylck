from datetime import datetime, timezone

import discord
import discord.utils
from zoneinfo import ZoneInfo

from discord.ext import commands
from discord import app_commands
from data import UserData
from sharing_codes import config
from team_management import init_load_user


class Attendence(commands.Cog):

    @app_commands.command(name="출석", description="출석하고 골드를 받습니다.")
    async def daily_attendance(self, interaction: discord.Interaction):
        if interaction.channel.id not in config().allowed_channel_id:
            await interaction.response.send_message(
                "이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True
            )
            return

        await interaction.response.defer()

        user = init_load_user(interaction)  # 사용자 로드

        # 현재 시간과 출석 기록 확인
        current_time_kst = discord.utils.utcnow().astimezone(
            ZoneInfo("Asia/Seoul")
        )  # 한국 시간으로 현재 시간 얻기

        # 마지막 출석 날짜 확인
        last_attendance_date = user.login_record.astimezone(ZoneInfo("Asia/Seoul"))

        # 이미 오늘 출석한 경우 처리
        if all(
            [
                last_attendance_date.year == current_time_kst.year,
                last_attendance_date.month == current_time_kst.month,
                last_attendance_date.day == current_time_kst.day,
            ]
        ):
            await interaction.followup.send(
                "오늘은 이미 출석했습니다. 내일 다시 출석해주세요!", ephemeral=True
            )
            return

        # 출석 처리 및 골드 지급
        user.update_balance(config().daily_reward)  # 골드 업데이트
        user.login_record = discord.utils.utcnow()  # 로그인 기록 추가

        # 출석 완료 메시지
        await interaction.followup.send(
            f"출석 완료! {config().daily_reward} 골드를 받았습니다. 현재 예산: {user.balance} 골드",
            ephemeral=False,
        )


# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(Attendence(bot))
