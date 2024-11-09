import discord
import asyncio
from discord import app_commands
from discord.ext import commands
from sharing_codes import COMMUNITY_CHANEL_ID
from data import UserData, users_collection


class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="맞다이", description="상대와 팀 가치로 대결을 합니다.")
    @app_commands.describe(opponent="맞다이 상대방 멘션")
    async def matchup(self, interaction: discord.Interaction, opponent: discord.Member):

        # 채널 ID 확인
        if interaction.channel.id not in COMMUNITY_CHANEL_ID:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
            return

        # 유저 데이터 로드
        user_data = UserData.load_from_db(interaction.user.id)
        opponent_data = UserData.load_from_db(opponent.id)

        # 팀 초기화 여부 확인
        if not user_data or user_data.team_value is None:
            await interaction.response.send_message("팀이 초기화되지 않았습니다. 먼저 선수를 등록하세요.", ephemeral=True)
            return
        if not opponent_data or opponent_data.team_value is None:
            await interaction.response.send_message(f"{opponent.display_name}님의 팀이 초기화되지 않았습니다.", ephemeral=True)
            return

        user_team_value = user_data.team_value
        opponent_team_value = opponent_data.team_value

        # 팀 가치 비교 진행 안내
        await interaction.response.send_message("팀 가치 계산 중...", ephemeral=False)
        await asyncio.sleep(1)
        await interaction.followup.send("맞다이 뜨는 중...", ephemeral=False)
        await asyncio.sleep(1)

        # 팀 가치 비교 결과 메시지
        if user_team_value > opponent_team_value:
            result = f"{interaction.user.display_name} vs. {opponent.display_name}, {interaction.user.display_name} 승리!"
        elif user_team_value < opponent_team_value:
            result = f"{interaction.user.display_name} vs. {opponent.display_name}, {interaction.user.display_name} 패배..."
        else:
            result = "무승부!"

        # 최종 결과 출력
        # 최종 결과 출력
        await interaction.followup.send(
            f"{interaction.user.display_name}님의 팀 가치: {user_team_value} 골드\n"
            f"{opponent.display_name}님의 팀 가치: {opponent_team_value} 골드\n\n{result}", ephemeral=False
        )

    @app_commands.command(name="랭킹", description="현재 서버의 팀가치 순위를 확인합니다.")
    async def ranking(self, interaction: discord.Interaction):
        # MongoDB에서 모든 사용자 로드
        users_with_team_value = list(users_collection.find().limit(10))

        if not users_with_team_value:
            await interaction.response.send_message("현재 데이터가 없습니다.", ephemeral=True)
            return

        # 랭킹 메시지 구성
        ranking_message = ["판타지 LCK 랭킹:"]
        for i, user_data in enumerate(users_with_team_value, start=1):
            # 사용자 데이터 로드
            user = UserData.load_from_db(user_data["user_id"])

            # 사용자가 등록한 선수들의 총 팀 가치 계산
            team_value = UserData.get_team_value()

            # 디스코드 사용자 정보 가져오기
            discord_user = await self.bot.fetch_user(user_data["discord_id"])

            # 랭킹 메시지에 추가
            ranking_message.append(f"{i}. {discord_user.display_name} - {team_value} 골드")

        # 랭킹 메시지 전송
        await interaction.response.send_message("\n".join(ranking_message), ephemeral=False)

# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(Ranking(bot))
