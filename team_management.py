import logging

from discord.ext import commands
from sharing_codes import UserData, PlayerData, initialize_user, register_players, players_data, is_registration_active, is_sale_active, user_data, ALLOWED_CHANNEL_ID, COMMUNITY_CHANEL_ID

pos_alias = {
    '탑': 'top',
    '정글': 'jgl',
    '미드': 'mid',
    '바텀': 'adc',
    '원딜': 'adc',
    '서폿': 'sup'
}

logger = logging.getLogger()
logger.debug(f"입력된 선수 이름: {PlayerData.name}")
logger.debug(f"유효한 선수 이름 목록: {list(players_data.keys())}")

@commands.command()
async def 선수등록(ctx, position: str, name: str):
    logger.debug(f"선수등록 함수 호출: position={position}, name={name}")

    if not is_registration_active:
        await ctx.send("현재 선수 등록이 비활성화 상태입니다.")
        return

    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    user = initialize_user(user_id)  # 사용자 초기화 및 가져오기

    # 선수 데이터 확인
    logger.debug(f"players_data = {players_data}")
    if name not in players_data.keys():
        logger.debug(f"{name} 선수는 올바른 이름이 아닙니다.")
        await ctx.send(f"{name} 선수 이름이 올바른 이름이 아닙니다.")
        return

    player_info = players_data[name]

    # 포지션 확인
    if player_info['position'] != position:
        logger.debug(f"{name} 선수의 포지션은 {player_info['position']}입니다.")
        await ctx.send(f"{name} 선수의 포지션은 {player_info['position']}입니다. 올바른 포지션을 입력해주세요.")
        return

    # 해당 포지션에 이미 선수가 있는지 확인
    if getattr(user, pos_alias[player_info['position']]) is not None:
        await ctx.send(f"{position} 포지션에는 이미 선수가 등록되어 있습니다.")
        return

    # 선수 등록 및 잔고 차감
    player = PlayerData(name, player_info['tier'])
    setattr(user, pos_alias[player_info['position']], player)
    
    # 예산 차감 로직 추가 (여기서 player.value가 필요합니다)
    user.__balance -= player.value  # 선수 등록 시 예산 차감
    await ctx.send(f"{name} 선수가 {position} 포지션에 등록되었습니다. 현재 예산: {user.balance} 골드")


@commands.command()
async def 선수판매(ctx, position: str = None):
    if not is_sale_active:
        await ctx.send("현재 선수 판매가 비활성화 상태입니다.")
        return
    
    if ctx.channel.id not in ALLOWED_CHANNEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    user = initialize_user(user_id)  # 사용자 초기화 및 가져오기

    # 'all!'이 입력되면 모든 포지션의 선수를 판매
    if position == "all":
        total_gold = 0
        for pos in ['탑', '정글', '미드', '원딜', '서폿']:
            player = getattr(user, pos_alias[pos])
            if player is not None:
                total_gold += player.value
                setattr(user, pos_alias[pos], None)  # 선수 판매
                logger.info(f"{player.name} 선수가 {pos} 포지션에서 판매되었습니다.")
        
        user.__balance += total_gold  # 총 금액을 유저의 예산에 추가
        await ctx.send(f"모든 선수가 판매되었습니다. {total_gold} 골드를 얻었습니다. 현재 예산: {user.balance} 골드")

    elif position in pos_alias:
        # 포지션에 특정 선수만 판매
        player = getattr(user, pos_alias[position])
        if player is None:
            await ctx.send(f"{position} 포지션에 등록된 선수가 없습니다.")
            return

        # 선수 판매
        setattr(user, pos_alias[position], None)
        user.__balance += player.value  # 선수 가치를 예산에 더함
        await ctx.send(f"{player.name} 선수가 판매되었습니다. {player.value} 골드를 얻었습니다. 현재 예산: {user.balance} 골드")
    
    else:
        await ctx.send(f"{position}은(는) 올바른 포지션이 아닙니다.")



@commands.command()
async def 내팀(ctx):
    if ctx.channel.id not in COMMUNITY_CHANEL_ID:
        await ctx.send("이 명령어는 지정된 채널에서만 사용할 수 있습니다.")
        return

    user_id = ctx.author.id
    initialize_user(user_id)

    user_info: UserData = user_data[user_id]

    team_info = user_info.team_data  # 팀 데이터 가져오기
    team_display = f"- 감독: {ctx.author.display_name}\n\n"

    # 팀 정보 반복
    for position, player in team_info.items():
        if player:  # 선수가 등록되어 있는 경우
            team_display += f"- {position}: {player.name} (가치: {player.value} 골드)\n"
        else:  # 선수가 등록되어 있지 않은 경우
            team_display += f"- {position}: 없음\n"

    # 총 팀 가치 및 예산 출력
    team_display += f"\n팀 가치: {user_info.team_value} 골드\n현재 예산: {user_info.balance} 골드"

    await ctx.send(team_display)


