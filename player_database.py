import json
import logging
import os
from sharing_codes import load_data, save_data, PlayerData, UserData

logger = logging.getLogger(__name__)

# 티어에 따른 가치 정의
TIER_VALUES = {
    "S": 50,
    "A": 40,
    "B": 30,
    "C": 20,
    "D": 10,
}


# 플레이어 추가
def add_player(user: UserData, name: str, position: str, tier: str):
    if tier not in TIER_VALUES:
        logger.error(f"정의되지 않은 티어: {tier}. 선수를 추가할 수 없습니다.")
        return

    # 새로운 PlayerData 인스턴스 생성
    player = PlayerData(name, tier)

    # 포지션에 따라 팀 데이터에 선수 추가
    if position == "탑":
        user.top = player
    elif position == "정글":
        user.jgl = player
    elif position == "미드":
        user.mid = player
    elif position == "원딜":
        user.adc = player
    elif position == "서폿":
        user.sup = player
    else:
        logger.error(f"유효하지 않은 포지션: {position}. 선수 추가 실패.")
        return

    logger.info(f"{name} 선수({position}, {tier} 등급)가 추가되었습니다.")



# 플레이어 업데이트
def update_player(user: UserData, name: str, position: str = None, tier: str = None):
    # 사용자 팀 데이터에서 선수를 찾기
    team_data = user.team_data
    player_to_update = None

    # 포지션에 따라 해당 선수 찾기
    for pos, player in team_data.items():
        if player and player.name == name:
            player_to_update = player
            current_position = pos
            break

    if player_to_update is None:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")
        return

    # 포지션 업데이트
    if position:
        if current_position != position:  # 포지션이 변경될 경우
            # 기존 포지션에서 제거
            setattr(user, current_position, None)
            # 새로운 포지션에 추가
            if position in ['탑', '정글', '미드', '원딜', '서폿']:
                setattr(user, position, player_to_update)
            else:
                logger.warning(f"유효하지 않은 포지션: {position}. 포지션 업데이트 생략합니다.")

    # 티어 업데이트
    if tier:
        if tier in TIER_VALUES:
            player_to_update.tier = tier  # PlayerData의 티어 업데이트
            logger.info(f"{name} 선수의 티어가 {tier}로 업데이트되었습니다.")
        else:
            logger.warning(f"정의되지 않은 티어: {tier}. 티어 업데이트를 생략합니다.")

    logger.info(f"{name} 선수 정보가 수정되었습니다.")



def delete_player(user: UserData, name: str):
    team_data = user.team_data
    player_to_delete = None
    current_position = None

    # 팀 데이터에서 삭제할 선수 찾기
    for pos, player in team_data.items():
        if player and player.name == name:
            player_to_delete = player
            current_position = pos
            break

    if player_to_delete is None:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")
        return

    # 해당 포지션에서 선수 제거
    setattr(user, current_position, None)
    logger.info(f"{name} 선수가 삭제되었습니다.")


def initialize_players(user: UserData):
    team_data = user.team_data

    # 팀 데이터에 플레이어가 없는 경우 초기화
    if all(player is None for player in team_data.values()):
        # 기본 플레이어 데이터 초기화
        for pos in team_data.keys():
            setattr(user, pos.lower(), None)  # 각 포지션 초기화
    
    logger.info("플레이어 데이터가 초기화되었습니다.")