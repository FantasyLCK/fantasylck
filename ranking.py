import discord
import asyncio
from discord import app_commands
from discord.ext import commands
from sharing_codes import config
from data import UserData, users_full_roster_collection
from roster_logic import RosterComparisonLogic, PointComparisonLogic


class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="맞다이", description="상대와 팀 가치로 대결을 합니다.")
    @app_commands.describe(opponent="맞다이 상대방 멘션")
    async def matchup(self, interaction: discord.Interaction, opponent: discord.Member):

        # 채널 ID 확인
        if interaction.channel.id not in config().community_channel_id:
            await interaction.response.send_message(
                "이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True
            )
            return

        # 유저 데이터 로드
        user_data: UserData
        opponent_data: UserData

        # 팀 초기화 여부 확인
        try:
            user_data = UserData.load_from_db(interaction.user.id)
            if not user_data.has_full_roster():
                await interaction.response.send_message(
                    "로스터가 완성되지 않았습니다. 먼저 선수를 등록하세요.",
                    ephemeral=True,
                )
                return
        except:
            await interaction.response.send_message(
                "팀이 초기화되지 않았습니다. 먼저 선수를 등록하세요.", ephemeral=True
            )
            return
        try:
            opponent_data = UserData.load_from_db(opponent.id)
            if not opponent_data.has_full_roster():
                await interaction.response.send_message(
                    "상대 팀의 로스터가 완성되지 않았습니다.", ephemeral=True
                )
                return
        except:
            await interaction.response.send_message(
                "상대 팀이 초기화되지 않았습니다.", ephemeral=True
            )
            return

        # 팀 가치 비교 진행 안내
        await interaction.response.send_message("팀 가치 계산 중...", ephemeral=False)
        await asyncio.sleep(1)
        await interaction.followup.send("맞다이 뜨는 중...", ephemeral=False)
        await asyncio.sleep(1)

        logic = PointComparisonLogic(user_data, opponent_data)
        logic_output = logic.determine_winner()

        # 팀 가치 비교 결과 메시지
        if logic_output > 0:
            result = f"{interaction.user.display_name} vs. {opponent.display_name}, {interaction.user.display_name} 승리!"
        elif logic_output < 0:
            result = f"{interaction.user.display_name} vs. {opponent.display_name}, {interaction.user.display_name} 패배..."
        else:
            result = "무승부!"

        # 최종 결과 출력
        # 최종 결과 출력
        await interaction.followup.send(
            f"{interaction.user.display_name}님의 팀 가치: {sum(logic.get_team1_values())} 골드\n"
            f"{opponent.display_name}님의 팀 가치: {sum(logic.get_team2_values())} 골드\n\n{result}",
            ephemeral=False,
        )

        pos_list = ["탑", "정글", "미드", "원딜", "서폿"]

        detailed_results = "**상세 맞다이 내역**\n"
        for i in range(5):
            detailed_results += f"- {pos_list[i]}: {user_data.roster[i].value}{f"(+{user_data.get_single_team_bonus()})" if user_data.single_team_roster else ""} (주사위: {logic.get_team1_offset()[i]}) vs {opponent_data.roster[i].value + (opponent_data.get_single_team_bonus() if opponent_data.single_team_roster else 0)} (주사위: {logic.get_team2_offset()[i]})\n"

        await interaction.followup.send(detailed_results, ephemeral=True)

    @app_commands.command(
        name="랭킹", description="현재 서버의 팀가치 순위를 확인합니다."
    )
    async def ranking(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        # MongoDB에서 모든 사용자 로드
        users_with_team_value = list(users_full_roster_collection().find())

        if not users_with_team_value:
            await interaction.response.send_message(
                "현재 데이터가 없습니다.", ephemeral=True
            )
            return

        users_data: list[UserData] = list()

        for i, users in enumerate(users_with_team_value):
            users_data.append(UserData(users["discord_id"]))

        sorted_users_data = sorted(users_data, key=lambda x: x.team_value + x.balance)
        sorted_users_data.reverse()

        # 랭킹 메시지 구성
        if len(sorted_users_data) == 0:
            await interaction.response.send_message(
                "판타지 LCK 랭킹이 비어 있습니다.", ephemeral=False
            )
        ranking_message = ["판타지 LCK 랭킹:"]
        for i in range(min(len(sorted_users_data), 10)):

            user_data = sorted_users_data[i]

            # 디스코드 사용자 정보 가져오기
            discord_user = await self.bot.fetch_user(user_data.discord_id)

            # 랭킹 메시지에 추가
            ranking_message.append(
                f"{i + 1}. {discord_user.display_name} - {user_data.team_value + user_data.balance} (팀 밸류: {user_data.team_value}, 잔고: {user_data.balance})"
            )

        # 랭킹 메시지 전송
        await interaction.followup.send("\n".join(ranking_message), ephemeral=False)


# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(Ranking(bot))
