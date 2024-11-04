import json
import os

# 데이터 파일 경로
DATA_FILE = "player_data.json"

# JSON 파일이 존재하지 않는 경우 빈 데이터 생성
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"players": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# 데이터를 JSON 파일로 저장
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

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


# 선수 데이터 등록
def register_players():
    data = load_data()  # 데이터 로드
    global players_data ; {
        "탑": {
            "S": ["도란", "기인"],
            "A": ["제우스", "킹겐"],
            "B": ["퍼펙트", "클리어"],
            "C": ["두두", "미하일"],
            "D": ["프로그", "모건"],
        },
        "정글": {
            "S": ["피넛", "캐니언"],
            "A": ["오너", "루시드"],
            "B": ["표식", "랩터"],
            "C": ["커즈", "실비"],
            "D": ["스폰지", "영재"],
        },
        "미드": {
            "S": ["제카", "쵸비"],
            "A": ["페이커", "쇼메이커"],
            "B": ["비디디", "클로저"],
            "C": ["불독", "피셔"],
            "D": ["예후", "페이트"],
        },
        "원딜": {
            "S": ["바이퍼", "페이즈"],
            "A": ["구마유시", "에이밍"],
            "B": ["데프트", "헤나"],
            "C": ["리퍼", "지우"],
            "D": ["테디", "엔비"],
        },
        "서폿": {
            "S": ["딜라이트", "리헨즈"],
            "A": ["케리아", "켈린"],
            "B": ["베릴", "듀로"],
            "C": ["안딜", "구거"],
            "D": ["플레타", "폴루"]
        }
    }

    for position, tiers in players_data.items():
        for tier, players in tiers.items():
            for name in players:
                # 각 선수의 정보를 데이터에 추가
                data["players"][name] = {
                    "position": position,
                    "tier": tier,
                    "value": TIER_VALUES[tier]  # 티어에 따라 가치 설정
                }

    save_data(data)  # 선수 정보를 파일에 저장
