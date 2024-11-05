from discord.ext import commands
from sharing_codes import UserData, PlayerData, initialize_user, register_players, is_registration_active, is_sale_active, user_data, ALLOWED_CHANNEL_ID

@commands.command()
async def 선수등록(ctx, position: str, name: str):
    if not is_registration_active:
        await ctx.send("현재 선수 등록이 비활성화 상태입니다.")
        return
    
    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    user = initialize_user(user_id)  # 사용자 초기화 및 가져오기

    # 선수 데이터 확인
    players_data = register_players()
    if position not in players_data or name not in [player.name for player in players_data[position]]:
        await ctx.send(f"{name}는 유효한 선수 이름이 아닙니다.")
        return

    # 해당 포지션에 이미 선수가 있는지 확인
    if getattr(user, position) is not None:
        await ctx.send(f"{position} 포지션에는 이미 선수가 등록되어 있습니다.")
        return

    # 선수 등록 및 잔고 차감
    tier = next((tier for tier, players in players_data[position].items() if name in players), None)
    player = PlayerData(name, tier)
    setattr(user, position, player)
    user.balance -= player.value
    
    await ctx.send(f"{name} 선수가 {position} 포지션에 등록되었습니다. 현재 예산: {user.balance} 골드")


@commands.command()
async def 선수판매(ctx, position: str):
    if not is_sale_active:
        await ctx.send("현재 선수 등록이 비활성화 상태입니다.")
        return
    
    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    user = initialize_user(user_id)  # 사용자 초기화 및 가져오기

    # 포지션에 선수 확인
    player = getattr(user, position)
    if player is None:
        await ctx.send(f"{position} 포지션에 등록된 선수가 없습니다.")
        return

    # 선수 판매 및 예산 갱신
    user.balance += player.value
    setattr(user, position, None)
    
    await ctx.send(f"{player.name} 선수가 판매되었습니다. {player.value} 골드를 얻었습니다. 현재 예산: {user.balance} 골드")


@commands.command()
async def 내팀(ctx):
    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    initialize_user(user_id)

    team_info = user_data[user_id].team_data  # 팀 데이터 가져오기
    team_display = f"감독: {ctx.author.display_name}\n\n"
    total_team_value = 0

    # 팀 정보 반복
    for position, player in team_info.items():
        if player:  # 선수가 등록되어 있는 경우
            team_display += f"{position}: {player.name} (가치: {player.value} 골드)\n"
            total_team_value += player.value
        else:  # 선수가 등록되어 있지 않은 경우
            team_display += f"{position}: 없음\n"

    UserData.team_value = total_team_value  # 팀 가치 설정
    team_display += f"\n팀 가치: {total_team_value} 골드\n현재 예산: {UserData.balance} 골드"

    await ctx.send(team_display)

