from discord.ext import commands
from sharing_codes import user_data, user_budgets, players_data, is_registration_active, is_sale_active, initialize_user, register_players, get_player_value, load_data, save_data, TIER_VALUES, ALLOWED_CHANNEL_ID, COMMUNITY_CHANEL_ID

@commands.command()
async def 선수등록(ctx, position, player):
    if not is_registration_active:
        await ctx.send("현재 선수 등록이 비활성화 상태입니다.")
        return

    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return
    
    user_id = ctx.author.id
    initialize_user(user_id)  # Initialize the user's data

    # 포지션과 선수 존재 여부 확인
    if position not in players_data:
        await ctx.send(f"{position} 포지션은 존재하지 않습니다.")
        return
    
    # 선수 찾기
    for tier, players in players_data[position].items():
        if player in players:
            player_tier = tier
            player_value = TIER_VALUES[tier]
            user_data[user_id]["team"][position] = {
                "name": player,
                "tier": player_tier,
                "value": player_value
            }
            user_budgets[user_id] -= player_value  # Subtract player value from user budget
            save_data(user_data)
            await ctx.send(f"{position} 포지션의 {player} 선수가 등록되었습니다.")
            return

    await ctx.send(f"{position} 포지션에 {player} 선수가 존재하지 않습니다.")

@commands.command()
async def 선수판매(ctx, position=None):
    if not is_sale_active:
        await ctx.send("현재 선수 판매가 비활성화 상태입니다.")
        return

    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자 초기화

    if position == "all":
        total_value = 0
        for pos, player in user_data[user_id]["team"].items():
            if player:
                total_value += player["value"]
                user_data[user_id]["team"][pos] = None
        user_budgets[user_id] += total_value  # Add total value to user budget
        user_data[user_id]["team_value"] -= total_value
        await ctx.send("모든 선수가 판매되었습니다.")
    else:
        if position not in user_data[user_id]["team"] or user_data[user_id]["team"][position] is None:
            await ctx.send(f"{position} 포지션에 선수가 없습니다.")
            return
        name = user_data[user_id]["team"][position]["name"]
        player_value = user_data[user_id]["team"][position]["value"]
        user_budgets[user_id] += player_value
        user_data[user_id]["team_value"] -= player_value
        user_data[user_id]["team"][position] = None
        await ctx.send(f"{position} 포지션의 {name} 선수가 판매되어 {player_value} 골드가 반환되었습니다.")


@commands.command()
async def 내팀(ctx):
    if ctx.channel.id not in COMMUNITY_CHANEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return
    
    user_id = ctx.author.id
    user_name = ctx.author.display_name 
    initialize_user(user_id)

    # 현재 팀 정보 가져오기
    team_info = user_data[user_id]["team"]
    team_display = f"감독: {user_name}\n\n"
    total_team_value = 0

    for position, player in team_info.items():
        if player:
            team_display += f"{position}: {player['name']} (가치: {player['value']} 골드)\n"
            total_team_value += player["value"]
        else:
            team_display += f"{position}: 없음\n"

    # 팀 가치 업데이트
    user_data[user_id]["team_value"] = total_team_value
    team_display += f"\n팀 가치: {total_team_value} 골드\n"
    team_display += f"현재 예산: {user_budgets[user_id]} 골드"

    await ctx.send(team_display)