import logging
from discord.ext import commands
from discord import app_commands
import discord
from sharing_codes import UserData, PlayerData, initialize_user, load_data, save_data, user_data, TIER_VALUES, ALLOWED_CHANNEL_ID, COMMUNITY_CHANEL_ID

pos_alias = {
    '탑': 'top',
    '정글': 'jgl',
    '미드': 'mid',
    '바텀': 'adc',
    '원딜': 'adc',
    '서폿': 'sup'
}

logger = logging.getLogger()

class TeamManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="선수등록", description="해당 포지션의 선수를 내 팀에 등록합니다.")
    @app_commands.describe(position="선수를 등록할 포지션", name="등록할 선수의 이름")
    async def purchase_player(self, interaction: discord.Interaction, position: str, name: str):
        logger.debug(f"선수등록 함수 호출: position={position}, name={name}")

        # 선수 등록 활성화 체크
        if interaction.channel.id not in ALLOWED_CHANNEL_ID:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
            return

        user_id = interaction.user.id
        user = initialize_user(user_id)  # 사용자 초기화

        # JSON에서 선수 데이터 로드
        data = load_data()  # 플레이어 데이터를 JSON에서 불러오기
        if name not in data['players']:
            logger.debug(f"{name} 선수는 올바른 이름이 아닙니다.")
            await interaction.response.send_message(f"{name} 선수는 올바른 이름이 아닙니다.", ephemeral=True)
            return

        player_info = data['players'][name]

        # 포지션 확인
        if player_info['position'] != position:
            await interaction.response.send_message(f"{name} 선수의 포지션은 {player_info['position']}입니다. 올바른 포지션을 입력해주세요.", ephemeral=True)
            return

        # 해당 포지션에 이미 선수가 있는지 확인
        if getattr(user, pos_alias[player_info['position']]) is not None:
            await interaction.response.send_message(f"{position} 포지션에는 이미 선수가 등록되어 있습니다.", ephemeral=True)
            return

        # 잔고 확인
        if user.balance < PlayerData(name, player_info['tier']).value:
            await interaction.response.send_message(f"잔고가 부족합니다. 현재 예산: {user.balance}골드", ephemeral=True)
            return

        # 선수 등록 및 잔고 차감
        player = PlayerData(name, player_info['tier'])
        setattr(user, pos_alias[player_info['position']], player)

        await interaction.response.send_message(f"{name} 선수가 {position} 포지션에 등록되었습니다. 현재 예산: {user.balance} 골드", ephemeral=False)

    # 선수의 티어에 따라 비용을 계산하는 함수
    def get_player_cost(tier: str) -> int:
        tier_costs = {
            'S': 50,
            'A': 40,
            'B': 30,
            'C': 20,
            'D': 10
        }
        return tier_costs.get(tier, 0)

    @app_commands.command(name="선수판매", description="해당 포지션의 선수를 판매합니다.")
    @app_commands.describe(position="판매할 선수의 포지션. 'all'을 입력하면 모든 선수를 판매합니다")
    async def sell_player(self, interaction: discord.Interaction, position: str = None):
        if interaction.channel.id not in ALLOWED_CHANNEL_ID:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
            return

        user_id = interaction.user.id
        user = initialize_user(user_id)  # 사용자 초기화

        # 'all'이 입력되면 모든 포지션의 선수를 판매
        if position == "all":
            total_gold = 0
            for pos in ['탑', '정글', '미드', '원딜', '서폿']:
                player = getattr(user, pos_alias[pos])
                if player is not None:
                    total_gold += player.value
                    setattr(user, pos_alias[pos], None)  # 선수 판매
                    logger.info(f"{player.name} 선수가 {pos} 포지션에서 판매되었습니다.")
            
            await interaction.response.send_message(f"모든 선수가 판매되었습니다. {total_gold} 골드를 얻었습니다. 현재 예산: {user.balance} 골드", ephemeral=True)

        elif position in pos_alias:
            # 포지션에 특정 선수만 판매
            player = getattr(user, pos_alias[position])
            if player is None:
                await interaction.response.send_message(f"{position} 포지션에 등록된 선수가 없습니다.", ephemeral=True)
                return

            # 선수 판매
            setattr(user, pos_alias[position], None)
            
            await interaction.response.send_message(f"{player.name} 선수가 판매되었습니다. {player.value} 골드를 얻었습니다. 현재 예산: {user.balance} 골드", ephemeral=True)

        else:
            await interaction.response.send_message(f"{position}은(는) 올바른 포지션이 아닙니다.", ephemeral=True)

    @app_commands.command(name="내팀", description="현재 등록된 팀을 확인합니다")
    async def myteam(self, interaction: discord.Interaction):
        if interaction.channel.id not in COMMUNITY_CHANEL_ID:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=False)
            return

        user_id = interaction.user.id
        initialize_user(user_id)

        user_info: UserData = user_data[user_id]

        team_info = user_info.team_data  # 팀 데이터 가져오기
        team_display = f"- 감독: {interaction.user.display_name}\n\n"

        # 팀 정보 반복
        for position, player in team_info.items():
            if player:  # 선수가 등록되어 있는 경우
                team_display += f"- {position}: {player.name} (가치: {player.value} 골드)\n"
            else:  # 선수가 등록되어 있지 않은 경우
                team_display += f"- {position}: 없음\n"

        # 총 팀 가치 및 예산 출력
        team_display += f"\n팀 가치: {user_info.team_value} 골드\n현재 예산: {user_info.balance} 골드"

        await interaction.response.send_message(team_display, ephemeral=True)

# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(TeamManagement(bot))
