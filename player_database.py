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


# 선순 추가
def add_player(name, position, tier):
    data = load_data()  # 데이터 로드
    if tier not in TIER_VALUES:
        logger.error(f"정의되지 않은 티어: {tier}. 선수를 추가할 수 없습니다.")
        return

    # PlayerData 객체 생성
    player = PlayerData(name, tier)

    # 선수 데이터를 업데이트
    data["players"][name] = {
        "position": position,
        "tier": player.tier,
        "value": player.value,
    }

    # 데이터 저장
    save_data(data)  
    logger.info(f"{player.name} 선수({position}, {player.tier} 등급)가 추가되었습니다.")



# 선수 수정
def update_player(user: UserData, name: str, position: str = None, tier: str = None):
    # 사용자 팀 데이터에서 선수를 찾기
    player_to_update = None
    current_position = None

    # 포지션에 따라 해당 선수 찾기
    for pos, player in user.team_data.items():
        if player and player.name == name:
            player_to_update = player
            current_position = pos
            break

    if player_to_update is None:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")
        return

    # 포지션 업데이트
    if position and current_position != position:  # 포지션이 변경될 경우
        # 기존 포지션에서 제거
        setattr(user, current_position, None)

        # 새로운 포지션에 추가
        if position in ['탑', '정글', '미드', '원딜', '서폿']:
            setattr(user, position, player_to_update)
            logger.info(f"{name} 선수가 {current_position}에서 {position}로 이동했습니다.")
        else:
            logger.warning(f"유효하지 않은 포지션: {position}. 포지션 업데이트 생략합니다.")

    # 티어 업데이트
    if tier:
        try:
            player_to_update.tier = tier  # PlayerData의 티어 업데이트
            logger.info(f"{name} 선수의 티어가 {tier}로 업데이트되었습니다.")
        except ValueError:
            logger.warning(f"정의되지 않은 티어: {tier}. 티어 업데이트를 생략합니다.")

    logger.info(f"{name} 선수 정보가 수정되었습니다.")

def remove_player(name: str):
    data = load_data()  # 데이터 로드
    
    if name in data["players"]:
        del data["players"][name]  # 선수 삭제
        save_data(data)  # 데이터 저장
        logger.info(f"{name} 선수가 삭제되었습니다.")
    else:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")


def initialize_players(user: UserData):
    team_data = user.team_data

    # 팀 데이터에 플레이어가 없는 경우 초기화
    if all(player is None for player in team_data.values()):
        # 기본 플레이어 데이터 초기화
        for pos in team_data.keys():
            setattr(user, pos.lower(), None)  # 각 포지션 초기화
    
    logger.info("플레이어 데이터가 초기화되었습니다.")