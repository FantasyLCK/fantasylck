from discord.ext import commands
from sharing_codes import user_data, is_registration_active, is_sale_active
from player_database import add_player, update_player, delete_player

@commands.command()
@commands.has_permissions(administrator=True)
async def 선수추가(ctx, name: str, position: str, tier: str):
    add_player(name, position, tier)
    await ctx.send(f"{name} 선수가 추가되었습니다.")

@commands.command()
@commands.has_permissions(administrator=True)
async def 선수수정(ctx, name: str, position: str = None, tier: str = None):
    update_player(name, position, tier)
    await ctx.send(f"{name} 선수 정보가 수정되었습니다.")

@commands.command()
@commands.has_permissions(administrator=True) 
async def 선수삭제(ctx, name: str):
    delete_player(name)
    await ctx.send(f"{name} 선수가 삭제되었습니다.")

@commands.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def on(ctx):
    global is_registration_active, is_sale_active
    is_registration_active = True
    is_sale_active = True
    await ctx.send("선수 등록 및 판매가 활성화되었습니다.")

@commands.command()
@commands.has_permissions(administrator=True)  # 관리자 권한 확인
async def off(ctx):
    global is_registration_active, is_sale_active
    is_registration_active = False
    is_sale_active = False
    await ctx.send("선수 등록 및 판매가 비활성화되었습니다.")