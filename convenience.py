from discord.ext import commands
from sharing_codes import PlayerData, players_data, TIER_VALUES, ALLOWED_CHANNEL_ID

@commands.command()
async def 선수목록(ctx, position):
    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    if position not in players_data:
        await ctx.send(f"{position} 포지션에 해당하는 선수가 없습니다.")
        return

    # 포지션에 해당하는 선수 불러오기
    tiered_players = {}
    for tier, players in players_data[position].items():
        tiered_players[tier] = players

    output = f"**{position} 포지션 선수 목록:**\n\n"
    for tier, players in sorted(tiered_players.items(), key=lambda x: TIER_VALUES[x[0]], reverse=True):
        players_list = ", ".join(players)
        gold_value = TIER_VALUES[tier]
        output += f"{tier} ({gold_value}골드) | {players_list}\n"

    await ctx.send(output)


@commands.command()
async def 명령어(ctx):

    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return
    
    commands_list = """
    **사용 가능한 명령어:**

    **!선수등록 [포지션] [선수명]**: 지정된 포지션에 선수를 등록합니다. ex) !선수등록 미드 페이커
    **!선수판매 [포지션]**: 지정된 포지션의 선수를 판매합니다. 'all'을 입력하면 모든 선수가 판매됩니다. ex) !선수판매 미드
    **!선수목록 [포지션]**: 해당 포지션의 선수 목록과 가치를 확인합니다. ex) !선수목록 미드
    **!내팀**: 현재 등록된 팀과 예산을 확인합니다.

    **!육구놀이**: 15골드를 지불하고 간단한 미니게임을 진행합니다. '!육구놀이룰'을 통해 규칙을 확인 할 수 있어요!
    **!출석**: 하루에 한 번 출석하여 5골드를 수령합니다.

    **!맞다이 [상대 아이디]**: 상대와 팀가치를 비교해 대결을 합니다.

    만든이: 다운사람 (www.instagram.com/lolsonam80)
    """
    await ctx.send(commands_list)

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

@commands.command()
async def 육구놀이룰(ctx):

    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    gamerule = """
    **육구놀이 룰**

    333 - 0골드
    369 - 30골드 (단, 순서대로)
    666 - 50골드
    999 - 100골드
    33X - 10골드
    66X - 20골드
    99X - 30골드
    """
    await ctx.send(gamerule)
