import discord
from discord.ext import commands
from sharing_codes import user_data, COMMUNITY_CHANEL_ID
import asyncio

@commands.command()
async def 맞다이(ctx, opponent: discord.Member):
    if ctx.channel.id not in COMMUNITY_CHANEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    opponent_id = opponent.id

    # 양 팀 초기화 확인
    if user_id not in user_data or user_data[user_id].team_value is None:
        await ctx.send("팀이 초기화되지 않았습니다. 먼저 선수를 등록하세요.")
        return
    if opponent_id not in user_data or user_data[opponent_id].team_value is None:
        await ctx.send(f"{opponent.display_name}님의 팀이 초기화되지 않았습니다.")
        return

    user_team_value = user_data[user_id].team_value
    opponent_team_value = user_data[opponent_id].team_value

    # 팀 가치 비교
    await ctx.send("팀 가치 계산 중...")
    await asyncio.sleep(1)
    await ctx.send("맞다이 뜨는 중...")
    await asyncio.sleep(1)

    if user_team_value > opponent_team_value:
        result = f"{ctx.author.display_name} vs. {opponent.display_name}, {ctx.author.display_name} 승리!"
    elif user_team_value < opponent_team_value:
        result = f"{ctx.author.display_name} vs. {opponent.display_name}, {ctx.author.display_name} 패배..."
    else:
        result = "무승부!"

    await ctx.send(f"{ctx.author.display_name}님의 팀가치: {user_team_value} 골드\n"
                   f"{opponent.display_name}님의 팀가치: {opponent_team_value} 골드\n\n{result}")


@commands.command()
async def 랭킹(ctx):
    if not user_data:
        await ctx.send("현재 데이터가 없습니다.")
        return

    ranking = sorted(
        ((user_id, data.team_value) for user_id, data in user_data.items()),
        key=lambda x: x[1],
        reverse=True
    )

    top_10 = ranking[:10]
    ranking_message = ["판타지 LCK 랭킹:"]
    for i, (u_id, team_value) in enumerate(top_10, start=1):
        user = await ctx.bot.fetch_user(u_id)
        ranking_message.append(f"{i}. {user.display_name} - {team_value} 골드")

    await ctx.send("\n".join(ranking_message))