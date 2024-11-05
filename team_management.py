from discord.ext import commands
from sharing_codes import UserData, PlayerData, initialize_user, register_players, user_data, user_budgets, is_registration_active, is_sale_active, ALLOWED_CHANNEL_ID, COMMUNITY_CHANEL_ID

@commands.command()
async def 선수등록(ctx, position: str, name: str):
    if not is_registration_active:
        await ctx.send("현재 선수 판매가 비활성화 상태입니다.")
        return
    
    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자를 초기화

    # 선수 등록 로직
    players_data = register_players()
    if position not in players_data or name not in [player.name for player in players_data[position]]:
        await ctx.send(f"{name}는 유효한 선수 이름이 아닙니다.")
        return

    if getattr(user_data[user_id], f'_UserData__{position}') is not None:
        await ctx.send(f"{position} 포지션에는 이미 선수가 등록되어 있습니다.")
        return

    tier = next(tier for tier, players in players_data[position].items() if name in players)
    setattr(user_data[user_id], f'_UserData__{position}', PlayerData(name, tier))
    
    await ctx.send(f"{name} 선수가 {position} 포지션에 등록되었습니다.")


@commands.command()
async def 선수판매(ctx, position: str):
    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자를 초기화

    # Check if player exists
    player = getattr(user_data[user_id], f'_UserData__{position}')
    if player is None:
        await ctx.send(f"{position} 포지션에 등록된 선수가 없습니다.")
        return

    # Sell the player
    user_data[user_id].balance += player.value
    setattr(user_data[user_id], f'_UserData__{position}', None)  # Set the position to None
    
    await ctx.send(f"{player.name} 선수가 판매되었습니다. {player.value} 골드를 얻었습니다.")


@commands.command()
async def 내팀(ctx):
    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    initialize_user(user_id)

    team_info = user_data[user_id].team_data
    team_display = f"감독: {ctx.author.display_name}\n\n"
    total_team_value = 0

    for position, player in team_info.items():
        if player:
            team_display += f"{position}: {player.name} (가치: {player.value} 골드)\n"
            total_team_value += player.value
        else:
            team_display += f"{position}: 없음\n"

    user_data[user_id].team_value = total_team_value  # Set team value
    team_display += f"\n팀 가치: {total_team_value} 골드\n현재 예산: {user_data[user_id].balance} 골드"

    await ctx.send(team_display)