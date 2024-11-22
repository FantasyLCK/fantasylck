import logging

logger = logging.getLogger(__name__)

# 티어에 따른 가치 정의
TIER_VALUES = {
    "S": 50,
    "A": 40,
    "B": 30,
    "C": 20,
    "D": 10,
}

# 데이터 파일 경로
DATA_FILE = "players_data.json"


# 선수 추가
def add_player(name: str, position: str, tier: str):
    data = load_data()  # 데이터 로드
    logger.debug(f"players_data = {data['players']}")

    if tier not in TIER_VALUES:
        logger.error(f"정의되지 않은 티어: {tier}. 선수를 추가할 수 없습니다.")
        return

    # PlayerData 객체 생성
    player = PlayerData(name, tier)

    # players_data에 PlayerData 객체 추가
    data["players"][name] = {
        "position": position,
        "tier": player.tier,
        "value": player.value,
    }

    # 데이터 저장
    save_data(data)
    logger.info(f"{name} 선수({position}, {tier} 등급)가 추가되었습니다.")
    logger.debug(f"업데이트된 players_data = {data['players']}")


# 선수 수정
def update_player(name: str, position: str = None, tier: str = None):
    data = load_data()  # 전체 데이터 로드
    logger.debug(f"현재 players_data: {data['players']}")

    # 전체 데이터에서 해당 선수 찾기
    if name not in data["players"]:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")
        return

    # 포지션 업데이트
    if position and data["players"][name]["position"] != position:
        if position in ["탑", "정글", "미드", "원딜", "서폿"]:
            data["players"][name]["position"] = position
            logger.info(f"{name} 선수가 {position} 포지션으로 이동했습니다.")
        else:
            logger.warning(
                f"유효하지 않은 포지션: {position}. 포지션 업데이트 생략합니다."
            )

    # 티어 업데이트
    if tier:
        try:
            data["players"][name]["tier"] = tier
            data["players"][name]["value"] = TIER_VALUES[tier]
            logger.info(f"{name} 선수의 티어가 {tier}로 업데이트되었습니다.")
        except KeyError:
            logger.warning(f"정의되지 않은 티어: {tier}. 티어 업데이트를 생략합니다.")

    save_data(data)  # 데이터 저장
    logger.debug(f"players_data = {data['players']}")


# 선수 삭제
def remove_player(name: str):
    data = load_data()  # 데이터 로드
    logger.debug(f"players_data = {data['players']}")

    if name in data["players"]:
        del data["players"][name]  # 선수 삭제
        save_data(data)  # 데이터 저장
        logger.info(f"{name} 선수가 삭제되었습니다.")
        logger.info("업데이트된 player_data: %s", data["players"])
    else:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")
