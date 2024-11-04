from discord.ext import commands
from player_database import load_data
from sharing_codes import user_data, user_budgets, initialize_user, register_players, get_player_value, ALLOWED_CHANNEL_ID

@commands.command()
async def 선수등록(ctx, position, name):

    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자 초기화
    register_players()

    # 선수 정보 확인
    try:
        players_data = load_data()["players"]  # 선수 데이터 로드
        player_info = next(({"name": name, "tier": players["tier"]} for player, players in players_data.items() 
                            if player == name), None)

        if player_info is None:
            await ctx.send("올바른 선수 이름을 입력하세요.")
            return

        player_value = get_player_value(name)

        # 예산 확인
        if player_value is None:
            await ctx.send("선수의 가치를 확인할 수 없습니다.")
            return

        if user_budgets[user_id] < player_value:
            await ctx.send(f"예산이 부족합니다. 현재 예산: {user_budgets[user_id]} 골드")
            return

        # 이미 등록된 포지션에 선수가 있으면 판매 후 등록
        if user_data[user_id]["team"][position] is not None:
            existing_player = user_data[user_id]["team"][position]
            user_budgets[user_id] += existing_player["value"]
            user_data[user_id]["team_value"] -= existing_player["value"]

        # 선수 등록
        user_data[user_id]["team"][position] = {"name": name, "value": player_value}
        user_budgets[user_id] -= player_value
        user_data[user_id]["team_value"] += player_value

        await ctx.send(f"{position}에 {name} 선수를 등록했습니다. 남은 예산: {user_budgets[user_id]} 골드")

    except KeyError as e:
        await ctx.send("선수 데이터를 로드하는 데 문제가 발생했습니다.")
        print(f"KeyError 발생: {e}")
    except Exception as e:
        await ctx.send("오류가 발생했습니다.")
        print(f"오류 발생: {e}")

@commands.command()
async def 선수판매(ctx, position=None):

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
        user_budgets[user_id] += total_value
        await ctx.send(f"모든 선수가 판매되었습니다.")
    else:
        if position not in user_data[user_id]["team"] or user_data[user_id]["team"][position] is None:
            await ctx.send(f"{position} 포지션에 선수가 없습니다.")
            return
        name = user_data[user_id]["team"][position]["name"]
        player_value = get_player_value(name)  # 가치를 업데이트
        user_data[user_id]["team"][position] = None  # 포지션의 선수를 삭제
        user_budgets[user_id] += player_value
        await ctx.send(f"{position} 포지션의 {name} 선수가 판매되어 {player_value} 골드가 반환되었습니다.")


@commands.command()
async def 내팀(ctx):

    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return
    
    user_id = ctx.author.id
    user_name = ctx.author.display_name 
    initialize_user(user_id)

    team_info = user_data[user_id]["team"]

    total_value = 0
    for pos, player in user_data[user_id]["team"].items():
        if player:
            total_value += player["value"]
            user_data[user_id]["team"][pos] = None
    user_budgets[user_id] += total_value

    team_display = f"감독: {user_name}\n\n"

    for position, player in team_info.items():
        if player:
            team_display += f"{position}: {player['name']} (가치: {player['value']} 골드)\n"
        else:
            f"{position}: 등록된 선수가 없습니다.\n"

    team_display += f"\n남은 예산: {user_budgets[user_id]} 골드\n팀 가치: {total_value} 골드"
    await ctx.send(team_display)
