import discord
from discord import app_commands
from discord.ext import commands
from sharing_codes import user_data, COMMUNITY_CHANEL_ID
import asyncio

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

        user_id = interaction.user.id
        opponent_id = opponent.id

        # 사용자의 팀 초기화 상태 확인
        if user_id not in user_data or user_data[user_id].team_value is None:
            await interaction.response.send_message("팀이 초기화되지 않았습니다. 먼저 선수를 등록하세요.", ephemeral=True)
            return
        if opponent_id not in user_data or user_data[opponent_id].team_value is None:
            await interaction.response.send_message(f"{opponent.display_name}님의 팀이 초기화되지 않았습니다.", ephemeral=True)
            return

        user_team_value = user_data[user_id].team_value
        opponent_team_value = user_data[opponent_id].team_value

        # 팀 가치 비교 과정 안내
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
        await interaction.followup.send(f"{interaction.user.display_name}님의 팀가치: {user_team_value} 골드\n"
                                        f"{opponent.display_name}님의 팀가치: {opponent_team_value} 골드\n\n{result}", ephemeral=False)

    @app_commands.command(name="랭킹", description="현재 서버의 팀가치 순위를 확인합니다.")
    async def ranking(self, interaction: discord.Interaction):
        if not user_data:
            await interaction.response.send_message("현재 데이터가 없습니다.", ephemeral=True)
            return

        # 팀 가치 기준 상위 10명의 랭킹 계산
        ranking = sorted(
            ((user_id, data.team_value) for user_id, data in user_data.items() if data.team_value is not None),
            key=lambda x: x[1],
            reverse=True
        )

        top_10 = ranking[:10]
        ranking_message = ["판타지 LCK 랭킹:"]
        for i, (u_id, team_value) in enumerate(top_10, start=1):
            user = await self.bot.fetch_user(u_id)
            ranking_message.append(f"{i}. {user.display_name} - {team_value} 골드")

        # 랭킹 메시지 전송
        await interaction.response.send_message("\n".join(ranking_message), ephemeral=False)

# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(Ranking(bot))
