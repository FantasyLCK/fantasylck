import logging
import discord 
from discord.ext import commands
from discord import app_commands
from sharing_codes import PlayerData, players_data, load_data, TIER_VALUES, ALLOWED_CHANNEL_ID, COMMUNITY_CHANEL_ID

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Convenience(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="선수목록", description="각 포지션의 선수와 가치를 확인합니다")
    @app_commands.describe(position="확인하고 싶은 포지션 (탑, 정글, 미드, 원딜, 서폿 중 하나)")
    async def player_list(self, interaction: discord.Interaction, position: str):
        if interaction.channel.id not in ALLOWED_CHANNEL_ID:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
            return

        # 최신 데이터 로드
        data = load_data()
        players_data = data["players"]  # 업데이트된 players_data 가져오기

        # 해당 포지션의 선수들만 필터링
        players_in_position = [
            (player, player_data) 
            for player, player_data in players_data.items() 
            if player_data['position'].lower() == position.lower()
        ]
        
        # 티어 순으로 정렬 (TIER_VALUES에 따라 정렬)
        players_in_position.sort(key=lambda x: TIER_VALUES[x[1]['tier']], reverse=True)

        # 출력 메시지 구성
        if players_in_position:
            output = f"### {position} 포지션 선수 목록:\n"
            for player, player_data in players_in_position:
                output += f"- {player}: {player_data['tier']} 티어 ({TIER_VALUES[player_data['tier']]} 골드)\n"
        else:
            output = f"{position} 포지션에 해당하는 선수가 없습니다."

        await interaction.response.send_message(output)

    @app_commands.command(name="명령어", description="사용 가능한 명령어 목록을 확인합니다.")
    async def show_commands(self, interaction: discord.Interaction):
        if interaction.channel.id not in COMMUNITY_CHANEL_ID:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=False)
            return

        commands_list = """
        **사용 가능한 명령어:**

        **/선수등록 [포지션] [선수명]**: 지정된 포지션에 선수를 등록합니다. ex) /선수등록 미드 페이커
        **/선수판매 [포지션]**: 지정된 포지션의 선수를 판매합니다. 'all'을 입력하면 모든 선수가 판매됩니다. ex) /선수판매 미드
        **/선수목록 [포지션]**: 해당 포지션의 선수 목록과 가치를 확인합니다. ex) /선수목록 미드
        **/내팀**: 현재 등록된 팀과 예산을 확인합니다.

        **/육구놀이**: 15골드를 지불하고 간단한 미니게임을 진행합니다. '/육구놀이룰'을 통해 규칙을 확인 할 수 있습니다.
        **/출석**: 하루에 한 번 출석하여 5골드를 수령합니다.

        **/맞다이 [@상대 아이디]**: 상대와 팀가치를 비교해 대결을 합니다. (상대방 멘션 필수)

        만든이: 다운사람
        도움주신분: ElectricalBoy
        """
        await interaction.response.send_message(commands_list, ephemeral=True)  # 본인만 볼 수 있도록

    @app_commands.command(name="육구놀이룰", description="육구놀이 규칙을 확인합니다.")
    async def gamerule(self, interaction: discord.Interaction):
        if interaction.channel.id not in ALLOWED_CHANNEL_ID:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=False)
            return

        gamerule = """
        **육구놀이 룰**

        ### 333 - 0골드
        ### 369 - 30골드 (단, 순서대로)
        ### 666 - 50골드
        ### 999 - 100골드
        ### 33X - 10골드
        ### 66X - 20골드
        ### 99X - 30골드

        **지나친 도박은 정신건강에 해롭읍니다.**
        """
        await interaction.response.send_message(gamerule)

# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(Convenience(bot))