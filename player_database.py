import json
import os
from sharing_codes import load_data, save_data, PlayerData


# 플레이어 추가
def add_player(name, position, tier):
    data = load_data()  # 데이터 로드
    data["players"][name] = {
        "position": position,
        "tier": tier,
    }
    save_data(data)  # 데이터 저장


# 티어에 따른 가치 정의
TIER_VALUES = {
    "S": 50,
    "A": 40,
    "B": 30,
    "C": 20,
    "D": 10,
}

# 플레이어 업데이트
def update_player(name=None, position=None, tier=None):
    data = load_data()  # 데이터 로드
    if name in data["players"]:
        if position:
            data["players"][name]["position"] = position
        
        if tier:
            data["players"][name]["tier"] = tier
            # 티어에 따라 가치 업데이트
            if tier in TIER_VALUES:
                data["players"][name]["value"] = TIER_VALUES[tier]
            else:
                print(f"정의되지 않은 티어: {tier}. 가치 업데이트를 생략합니다.")

        save_data(data)  # 데이터 저장
        print(f"{name} 선수 정보가 수정되었습니다.")
    else:
        print(f"{name} 선수를 찾을 수 없습니다.")


# 플레이어 삭제
def delete_player(name):
    data = load_data()  # 데이터 로드
    if name in data["players"]:
        del data["players"][name]
        save_data(data)  # 데이터 저장
        print(f"{name} 선수가 삭제되었습니다.")
    else:
        print(f"{name} 선수를 찾을 수 없습니다.")


# 선수 데이터 초기화
def initialize_players():
    data = load_data()
    if "players" not in data:
        data["players"] = {}
        save_data(data)
    return data["players"]
