from discord.ext import commands
from main import user_data, load_data, TIER_VALUES
from player_database import players_data
from sharing_codes import initialize_user

@commands.command()
async def 내팀보기(ctx):
    user_id = ctx.author.id
    user_id = ctx.author.id
    user_name = ctx.author.display_name  # Get the user's display name
    initialize_user(user_id)  # Initialize user if not already done

    team_info = user_data[user_id]["team"]
    budget = user_data[user_id]["budget"]
    team_value = user_data[user_id]["team_value"]

    team_display = f"감독: {user_name}\n\n"
    for position, player in team_info.items():
        if player:
            team_display += f"{position}: {player['name']} (가치: {player['value']} 골드)\n"
        else:
            f"{position}: 등록된 선수가 없습니다.\n"
    team_display += f"\n남은 예산: {budget} 골드\n팀 가치: {team_value} 골드"

@commands.command()
async def 선수목록(ctx, position):
    players_data = load_data()["players"]

    # 포지션에 해당하는 선수들을 티어별로 정리
    tiered_players = {}
    for name, data in players_data.items():
        if data["position"].lower() == position.lower():
            tier = data["tier"]
            if tier not in tiered_players:
                tiered_players[tier] = []
            tiered_players[tier].append(name)

    # 포지션에 선수가 없는 경우 처리
    if not tiered_players:
        await ctx.send(f"{position} 포지션에 해당하는 선수가 없습니다.")
        return

    # 티어별로 정렬하여 출력 형식 준비
    output = f"**{position} 포지션 선수 목록:**\n"
    for tier, players in sorted(tiered_players.items(), key=lambda x: TIER_VALUES[x[0]], reverse=True):
        players_list = ", ".join(players)
        gold_value = TIER_VALUES[tier]
        output += f"{tier} ({gold_value}골드) | {players_list}\n"

    await ctx.send(output)

@commands.command()
async def 명령어(ctx):
    commands_list = """
    **사용 가능한 명령어:**

    **!선수등록 [포지션] [선수명]**: 지정된 포지션에 선수를 등록합니다. ex) !선수등록 미드 페이커
    **!선수판매 [포지션]**: 지정된 포지션의 선수를 판매합니다. 'all'을 입력하면 모든 선수가 판매됩니다. ex) !선수판매 미드

    **!선수목록 [포지션]**: 해당 포지션의 선수 목록과 가치를 확인합니다. ex) !선수목록 미드
    **!내팀**: 현재 등록된 팀과 예산을 확인합니다.

    **!육구놀이**: 15골드를 지불하고 간단한 미니게임을 진행합니다. '!육구놀이룰'을 통해 규칙을 확인 할 수 있어요!
    **!출석**: 하루에 한 번 출석하여 5골드를 수령합니다.

    **!맞다이 [상대 아이디]**: 상대와 팀가치를 비교해 대결을 뜹니다.

    만든이: 다운사람 (www.instagram.com/lolsonam80)
    """
    await ctx.send('\n'.join(commands_list))

# 관리자 명령어 목록
@commands.command()
async def 관리자(ctx):
    manager_commands_list = """
    **관리자 전용 명령어:**

    **!선수추가 [이름] [포지션] [티어]**
    **!선수수정 [이름] [포지션] [티어]**
    **!선수삭제 [이름]**
    **!랭킹**
    **!on**: 이적시장 활성화
    **!off**: 이적시장 비활성화
    """
    await ctx.send(manager_commands_list)
