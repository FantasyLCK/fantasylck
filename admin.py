import discord
from discord.ext import commands
from discord import app_commands
from sharing_codes import is_registration_active, is_sale_active
from data_modification import add_player, update_player, remove_player

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="선수추가", description="선수를 추가합니다. (관리자 전용)")
    @app_commands.describe(name="선수 이름", position="선수 포지션", tier="선수 티어")
    @app_commands.default_permissions(administrator=True)  # 관리자 권한 확인
    async def 선수추가(self, interaction: discord.Interaction, name: str, position: str, tier: str, team: str, trait_weight: int):
        add_player(name, position, tier, team, trait_weight)
        await interaction.response.send_message(f"{name} 선수가 추가되었습니다.", ephemeral=True)

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
        remove_player(name)
        await interaction.response.send_message(f"{name} 선수가 삭제되었습니다.", ephemeral=True)

    @app_commands.command(name="on", description="선수 등록 및 판매를 활성화합니다. (관리자 전용)")
    @app_commands.default_permissions(administrator=True)  # 관리자 권한 확인
    async def on(self, interaction: discord.Interaction):
        global is_registration_active, is_sale_active
        is_registration_active = True
        is_sale_active = True
        await interaction.response.send_message("선수 등록 및 판매가 활성화되었습니다.", ephemeral=True)

    @app_commands.command(name="off", description="선수 등록 및 판매를 비활성화합니다. (관리자 전용)")
    @app_commands.default_permissions(administrator=True)  # 관리자 권한 확인
    async def off(self, interaction: discord.Interaction):
        global is_registration_active, is_sale_active
        is_registration_active = False
        is_sale_active = False
        await interaction.response.send_message("선수 등록 및 판매가 비활성화되었습니다.", ephemeral=True)

# Cog 등록 함수
async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
