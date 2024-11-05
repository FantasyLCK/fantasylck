import discord
from discord.ext import commands
from sharing_codes import user_data, initialize_user,COMMUNITY_CHANEL_ID
import asyncio

@commands.command()
async def 맞다이(ctx, opponent: discord.Member):
    if ctx.channel.id not in COMMUNITY_CHANEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

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
    user_id = ctx.author.id
    initialize_user(user_id)  # 사용자를 초기화

    # 현재 채널 멤버의 ID만 사용하여 랭킹을 계산
    channel_member_ids = {member.id for member in ctx.channel.members if not member.bot}
    
    # 사용자 데이터에서 팀 가치가 있는 사용자만 필터링
    ranking = []
    for user_id, data in user_data.items():
        if "team_value" in data and user_id in channel_member_ids:
            ranking.append((user_id, data["team_value"]))
            print(f"User ID: {user_id}, Team Value: {data['team_value']}")  # 디버깅 출력

    ranking = sorted(ranking, key=lambda x: x[1], reverse=True)

    # 탑10 정렬 및 사용자 랭크 찾기
    user_rank = next((i for i, (u_id, _) in enumerate(ranking, start=1) if u_id == user_id), None)
    top_10 = ranking[:10]

    # 랭킹 메시지 출력
    ranking_message = ["판타지 LCK 채널 랭킹:"]
    if top_10:  # 탑10이 존재할 경우에만 메시지 구성
        for i, (u_id, team_value) in enumerate(top_10, start=1):
            user = await ctx.bot.fetch_user(u_id)
            ranking_message.append(f"{i}. {user.display_name} - {team_value} 골드")
    else:
        ranking_message.append("현재 채널에 랭킹이 없습니다.")

    # 사용자가 탑10 외에 있을 경우 개인 순위 추가
    if user_rank and user_rank > 10:
        user = await ctx.bot.fetch_user(user_id)
        ranking_message.append(f"\n{user.display_name}님의 현재 순위: {user_rank}위 - {user_data[user_id]['team_value']} 골드")

    await ctx.send("\n".join(ranking_message))
