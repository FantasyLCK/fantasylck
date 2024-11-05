import json
import logging
import os
from sharing_codes import load_data, save_data, PlayerData

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
def add_player(name, position, tier):
    data = load_data()  # 데이터 로드
    if tier not in TIER_VALUES:
        logger.error(f"정의되지 않은 티어: {tier}. 선수를 추가할 수 없습니다.")
        return
    
    # PlayerData 객체를 생성하고 데이터를 JSON 형식으로 저장
    player = PlayerData(name, tier)
    data["players"][name] = {
        "position": position,
        "tier": player.tier,
        "value": player.value,
    }
    save_data(data)  # 데이터 저장
    logger.info(f"{name} 선수({position}, {tier} 등급)가 추가되었습니다.")


# 플레이어 업데이트
def update_player(name, position=None, tier=None):
    data = load_data()  # 데이터 로드
    if name in data["players"]:
        player_info = data["players"][name]

        # 포지션 업데이트
        if position:
            player_info["position"] = position
        
        # 티어 업데이트
        if tier:
            if tier in TIER_VALUES:
                player_info["tier"] = tier
                player_info["value"] = TIER_VALUES[tier]
                logger.info(f"{name} 선수의 티어가 {tier}로 업데이트되었습니다.")
            else:
                logger.warning(f"정의되지 않은 티어: {tier}. 가치 업데이트를 생략합니다.")

        save_data(data)  # 데이터 저장
        logger.info(f"{name} 선수 정보가 수정되었습니다.")
    else:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")


# 플레이어 삭제
def delete_player(name):
    data = load_data()  # 데이터 로드
    if name in data["players"]:
        del data["players"][name]
        save_data(data)  # 데이터 저장
        logger.info(f"{name} 선수가 삭제되었습니다.")
    else:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")


# 선수 데이터 초기화
def initialize_players():
    data = load_data()
    if "players" not in data:
        data["players"] = {}
        save_data(data)
    return data["players"]
