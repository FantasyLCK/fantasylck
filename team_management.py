import logging
from discord.ext import commands
from discord import app_commands
import discord
from sharing_codes import config
from data import UserData, PlayerData, get_player_cost


pos_alias = {
    '탑': 'top',
    '정글': 'jgl',
    '미드': 'mid',
    '바텀': 'adc',
    '원딜': 'adc',
    '서폿': 'sup'
}

logger = logging.getLogger()

def init_load_user(interaction: discord.Interaction) -> UserData:
    user_id = interaction.user.id
    user: UserData
    try:
        user = UserData.load_from_db(user_id)  # 사용자 로드
    except ValueError:
        user, result = UserData.create_new_entry(id=interaction.user.id, balance=150) # 새 사용자 DB에 저장
        logger.info(f"Initialized user data for user ID: {user_id}")
    return user

class TeamManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="선수등록", description="해당 포지션의 선수를 내 팀에 등록합니다.")
    @app_commands.describe(position="선수를 등록할 포지션", name="등록할 선수의 이름")
    async def purchase_player(self, interaction: discord.Interaction, position: str, name: str):
        logger.debug(f"선수등록 함수 호출: position={position}, name={name}")

        if interaction.channel.id not in config().allowed_channel_id:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
            return

        user = init_load_user(interaction)  # 사용자 로드

        if not config().is_registration_active:
            await interaction.response.send_message("현재 선수 등록이 비활성화되어 있습니다.", ephemeral=True)
            return

        # MongoDB에서 선수 데이터 로드
        player_data: PlayerData
        try:
            player_data = PlayerData.load_from_db(player_name=name)  # 이름으로 선수 데이터 로드
        except ValueError:
            logger.debug(f"{name} 선수는 올바른 이름이 아닙니다.")
            await interaction.response.send_message(f"{name} 선수는 올바른 이름이 아닙니다.", ephemeral=True)
            return

        # 포지션 확인
        if player_data.position != position:
            await interaction.response.send_message(f"{name} 선수의 포지션은 {player_data.position}입니다. 올바른 포지션을 입력해주세요.", ephemeral=True)
            return

        # 해당 포지션에 이미 선수가 있는지 확인
        if getattr(user, pos_alias[player_data.position]) is not None:
            await interaction.response.send_message(f"{position} 포지션에는 이미 선수가 등록되어 있습니다.", ephemeral=True)
            return

        # 잔고 확인
        player_cost = get_player_cost(player_data.tier)  # 선수 비용 계산
        if user.balance < player_cost:
            await interaction.response.send_message(f"골드가 부족합니다. 현재 예산: {user.balance}골드", ephemeral=True)
            return

        # 선수 등록 및 잔고 차감
        setattr(user, pos_alias[player_data.position] + "_id", player_data.id)
        user.update_balance(-player_cost)  # 골드 차감

        await interaction.response.send_message(f"{name} 선수가 {position} 포지션에 등록되었습니다. 현재 예산: {user.balance} 골드", ephemeral=True)

        
    @app_commands.command(name="선수판매", description="해당 포지션의 선수를 판매합니다.")
    @app_commands.describe(position="판매할 선수의 포지션. 'all'을 입력하면 모든 선수를 판매합니다")
    async def sell_player(self, interaction: discord.Interaction, position: str = None):
        if interaction.channel.id not in config().allowed_channel_id:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=True)
            return

        user = init_load_user(interaction)  # 사용자 로드

        if not config().is_sale_active:
            await interaction.response.send_message("현재 선수 판매가 비활성화되어 있습니다.", ephemeral=True)
            return

       # 'all'이 입력되면 모든 포지션의 선수를 판매
        if position == "all":
            total_gold = 0
            for pos in ['탑', '정글', '미드', '원딜', '서폿']:
                player = getattr(user, pos_alias[pos])
                if player is not None:
                    player_cost = get_player_cost(player.tier)  # 선수 비용 계산
                    total_gold += player_cost
                    user.sell_player(pos_alias[pos])  # 선수 판매
                    logger.info(f"{player.name} 선수가 {pos} 포지션에서 판매되었습니다.")

            await interaction.response.send_message(f"모든 선수가 판매되었습니다. {total_gold} 골드를 얻었습니다. 현재 예산: {user.balance} 골드", ephemeral=True)
        
        elif position in pos_alias:
            # 포지션에 특정 선수만 판매
            player = getattr(user, pos_alias[position])
            if player is None:
                await interaction.response.send_message(f"{position} 포지션에 등록된 선수가 없습니다.", ephemeral=True)
                return

            # 선수 판매
            player_cost = get_player_cost(player.tier)  # 선수 비용 계산
            user.sell_player(pos_alias[position])  # 선수 판매

            await interaction.response.send_message(f"{player.name} 선수가 판매되었습니다. {player_cost} 골드를 얻었습니다. 현재 예산: {user.balance} 골드", ephemeral=True)

        else:
            await interaction.response.send_message(f"{position}은(는) 올바른 포지션이 아닙니다.", ephemeral=True)

    @app_commands.command(name="내팀", description="현재 등록된 팀을 확인합니다")
    async def myteam(self, interaction: discord.Interaction):
        if interaction.channel.id not in config().community_channel_id:
            await interaction.response.send_message("이 명령어는 지정된 채널에서만 사용할 수 있습니다.", ephemeral=False)
            return

        user = init_load_user(interaction)  # 사용자 로드

        if not user:
            await interaction.response.send_message("팀 정보가 없습니다. 먼저 선수를 등록해주세요.", ephemeral=True)
            return
        
        team_info = {
            "탑": user.top,
            "정글": user.jgl,
            "미드": user.mid,
            "원딜": user.adc,
            "서폿": user.sup
        }

        team_display = f"- 감독: {interaction.user.display_name}\n\n"

        # 팀 정보 반복
        for position, player in team_info.items():
            if player:  # 선수가 등록되어 있는 경우
                team_display += f"- {position}: {player.name} (가치: {get_player_cost(player.tier)} 골드)\n"
            else:  # 선수가 등록되어 있지 않은 경우
                team_display += f"- {position}: 없음\n"

        # 총 팀 가치 및 예산 출력
        team_display += f"\n팀 가치: {user.team_value} 골드\n현재 예산: {user.balance} 골드"

        await interaction.response.send_message(team_display, ephemeral=True)

# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(TeamManagement(bot))
