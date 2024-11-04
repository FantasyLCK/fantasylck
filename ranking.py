import discord
from discord.ext import commands
from sharing_codes import user_data
import asyncio

@commands.command()
async def 맞다이(ctx, opponent: discord.Member):
    user_id = ctx.author.id
    opponent_id = opponent.id

    # 양 팀 초기화 확인
    if user_id not in user_data or "team_value" not in user_data[user_id]:
        await ctx.send("팀이 초기화되지 않았습니다. 먼저 선수를 등록하세요.")
        return
    if opponent_id not in user_data or "team_value" not in user_data[opponent_id]:
        await ctx.send(f"{opponent.display_name}님의 팀이 초기화되지 않았습니다.")
        return

    user_team_value = user_data[user_id]["team_value"]
    opponent_team_value = user_data[opponent_id]["team_value"]

    # 팀가치 비교
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
@commands.has_permissions(administrator=True)
async def 랭킹(ctx):
    # Check if there is any user data to rank
    if not user_data:
        await ctx.send("현재 데이터가 없습니다.")
        return
    
    guild_id = ctx.guild.id
    server_user_data = {user_id: data for user_id, data in user_data.items() if "guild_id" in data and data["guild_id"] == guild_id}
    
    if not server_user_data:
        await ctx.send("현재 서버에 등록된 사용자가 없습니다.")
        return


    # 서버 구성원 팀가치 정렬
    ranking = sorted(
        ((user_id, data["team_value"]) for user_id, data in server_user_data.items() if "team_value" in data),
        key=lambda x: x[1],
        reverse=True
    )

    # 탑10 정렬
    user_id = ctx.author.id
    user_rank = next((i for i, (u_id, _) in enumerate(ranking, start=1) if u_id == user_id), None)
    top_10 = ranking[:10]

    # 랭킹 메세지 출력
    ranking_message = ["판타지 LCK 랭킹:"]
    for i, (u_id, team_value) in enumerate(top_10, start=1):
        user = await ctx.bot.fetch_user(u_id)
        ranking_message.append(f"{i}. {user.display_name} - {team_value} 골드")

    # Include user's rank if they are not in the top 10
    if user_rank and user_rank > 10:
        user = await ctx.bot.fetch_user(user_id)
        ranking_message.append(f"\n{user.display_name}님의 현재 순위: {user_rank}위 - {user_data[user_id]['team_value']} 골드")

    await ctx.send("\n".join(ranking_message))
