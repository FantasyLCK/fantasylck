import discord
from discord.ext import commands
from discord import app_commands
from sharing_codes import config
from data_modification import add_player, update_player, remove_player
from ranking import UserData

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="선수추가", description="선수를 추가합니다. (관리자 전용)")
    @app_commands.describe(name="선수 이름", position="선수 포지션", tier="선수 티어")
    @app_commands.default_permissions(administrator=True)  # 관리자 권한 확인
    async def 선수추가(self, interaction: discord.Interaction, name: str, position: str, tier: str, team: str, trait_weight: int):
        if add_player(name, position, tier, team, trait_weight):
            await interaction.response.send_message(f"{name} 선수가 추가되었습니다.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{name} 선수를 추가할 수 없습니다.", ephemeral=True)

    @app_commands.command(name="선수수정", description="선수 정보를 수정합니다. (관리자 전용)")
    @app_commands.describe(name="선수 이름", position="새로운 포지션 (선택사항)", tier="새로운 티어 (선택사항)")
    @app_commands.default_permissions(administrator=True)  # 관리자 권한 확인
    async def 선수수정(self, interaction: discord.Interaction, name: str, position: str = None, tier: str = None):
        update_player(name, position, tier)
        await interaction.response.send_message(f"{name} 선수 정보가 수정되었습니다.", ephemeral=True)

    @app_commands.command(name="선수삭제", description="선수를 삭제합니다. (관리자 전용)")
    @app_commands.describe(name="선수 이름")
    @app_commands.default_permissions(administrator=True)  # 관리자 권한 확인
    async def 선수삭제(self, interaction: discord.Interaction, name: str):
        if remove_player(name):
            await interaction.response.send_message(f"{name} 선수가 삭제되었습니다.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{name} 선수를 삭제할 수 없습니다.", ephemeral=True)

    @app_commands.command(name="on", description="선수 등록 및 판매를 활성화합니다. (관리자 전용)")
    @app_commands.default_permissions(administrator=True)  # 관리자 권한 확인
    async def on(self, interaction: discord.Interaction):
        config().is_registration_active = True
        config().is_sale_active = True
        await interaction.response.send_message("선수 등록 및 판매가 활성화되었습니다.", ephemeral=True)

    @app_commands.command(name="off", description="선수 등록 및 판매를 비활성화합니다. (관리자 전용)")
    @app_commands.default_permissions(administrator=True)  # 관리자 권한 확인
    async def off(self, interaction: discord.Interaction):
        config().is_registration_active = False
        config().is_sale_active = False
        await interaction.response.send_message("선수 등록 및 판매가 비활성화되었습니다.", ephemeral=True)

    @app_commands.command(name="골드지급", description="득정 유저에게 골드를 지급합니다. (관리자 전용)")
    @app_commands.describe(target="대상 유저", amount="지급량")
    @app_commands.default_permissions(administrator=True)  # 관리자 권한 확인
    async def 골드지급(self, interaction: discord.Interaction, target: discord.Member, amount:str):
        try:
            gold_amount = max(0, int(amount))
            user_data = UserData.load_from_db(target.id)
            user_data.update_balance(gold_amount)
            await interaction.response.send_message(f"{target.display_name} 유저에게 {gold_amount} 골드가 지급되었습니다.", ephemeral=True)
        except:
            await interaction.response.send_message(f"골드 지급에 실패하였습니다.", ephemeral=True)

    @app_commands.command(name="골드몰수", description="득정 유저의 골드를 몰수합니다. (관리자 전용)")
    @app_commands.describe(target="대상 유저", amount="몰수량")
    @app_commands.default_permissions(administrator=True)  # 관리자 권한 확인
    async def 골드몰수(self, interaction: discord.Interaction, target: discord.Member, amount:str):
        try:
            user_data = UserData.load_from_db(target.id)
            gold_amount = min(user_data.balance, int(amount))
            user_data.update_balance(-gold_amount)
            await interaction.response.send_message(f"{target.display_name} 유저의 {gold_amount} 골드를 몰수하였습니다.", ephemeral=True)
        except:
            await interaction.response.send_message(f"골드 몰수에 실패하였습니다.", ephemeral=True)

# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
