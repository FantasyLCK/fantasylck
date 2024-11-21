import logging
from pymongo import DESCENDING
from sharing_codes import config
from data import PlayerData, TeamData, UserData, players_collection, users_collection, teams_collection
from team_management import pos_alias

logger = logging.getLogger(__name__)

# 선수 추가
def add_player(name: str, position: str, tier: str, team: str, trait_weight: int):
    if tier not in config().tier_values:
        logger.error(f"정의되지 않은 티어: {tier}. 선수를 추가할 수 없습니다.")
        return False

    if PlayerData.player_exists(player_name=name):
        logger.error(f"{tier} 선수가 이미 존재합니다.")
        return False

    # MongoDB에서 가장 최근에 추가된 player_id를 가져와서 +1
    last_player = players_collection().find_one(sort=[("player_id", DESCENDING)])
    new_player_id = (last_player["player_id"] + 1) if last_player else 1

    # PlayerData 객체 생성 및 MongoDB에 저장
    player = PlayerData.create_new_entry(
        id=new_player_id,
        name=name,
        position=position,
        team=team,
        tier=tier,
        trait_weight=trait_weight
    )

    logger.info(f"{name} 선수({position}, {tier} 등급)가 추가되었습니다.")
    logger.debug(f"새로운 선수 데이터: {player}")
    return True


# 선수 수정
def update_player(name: str, position: str = None, tier: str = None, pog_stack: str = None):
    player_data = players_collection().find_one({"name": name})

    if not player_data:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")
        return

    update_fields = {}

    # 포지션 업데이트
    if position and position in ['탑', '정글', '미드', '원딜', '서폿']:
        update_fields["position"] = position
        logger.info(f"{name} 선수가 {position} 포지션으로 이동했습니다.")
    elif position:
        logger.warning(f"유효하지 않은 포지션: {position}. 포지션 업데이트 생략합니다.")

    # 티어 업데이트
    if tier:
        if tier in config().tier_values:
            update_fields["tier"] = tier
            logger.info(f"{name} 선수의 티어가 {tier}로 업데이트되었습니다.")
        else:
            logger.warning(f"정의되지 않은 티어: {tier}. 티어 업데이트를 생략합니다.")

    if pog_stack is not None:
        try:
            pog_stack_val = int(pog_stack)
            player_data = PlayerData.load_from_db(player_name=name)
            player_data.pog_stacks = pog_stack_val
        except:
            logger.warning(f"올바르지 않은 POG 스택: {pog_stack}. POG 스택 업데이트를 생략합니다.")

    # 업데이트 필드가 있는 경우 MongoDB에 적용
    if update_fields:
        players_collection().update_one({"name": name}, {"$set": update_fields})
        logger.debug(f"{name} 선수 업데이트된 데이터: {update_fields}")

# 선수 거래 여부 수정
def update_player_availability(name: str, purchasable: bool = None, sellable: bool = None):
    player_data = players_collection().find_one({"name": name})

    if not player_data:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")
        return

    update_fields = {}

    if purchasable is not None:
        update_fields["purchasable"] = purchasable
    if sellable is not None:
        update_fields["sellable"] = sellable

    # 업데이트 필드가 있는 경우 MongoDB에 적용
    if len(update_fields) > 0:
        players_collection().update_one({"name": name}, {"$set": update_fields})
        logger.debug(f"{name} 선수 업데이트된 데이터: {update_fields}")


# 선수 삭제
def remove_player(name: str):
    try:
        player_data = PlayerData.load_from_db(player_name=name)
        for user in users_collection().find({pos_alias[player_data.position]: player_data.id}):
            user_data = UserData(user['discord_id'])
            user_data.sell_player(pos_alias[player_data.position])
        return True
    except ValueError:
        logger.error(f"{name} 선수를 찾을 수 없습니다.")
        return False

# 팀 추가
def add_team(name: str, placement: int):

    if TeamData.team_exists(name=name):
        logger.error(f"{name} 팀이 이미 존재합니다.")
        return False

    # MongoDB에서 가장 최근에 추가된 player_id를 가져와서 +1
    last_team = teams_collection().find_one(sort=[("id", DESCENDING)])
    new_team_id = (last_team["id"] + 1) if last_team else 1

    # PlayerData 객체 생성 및 MongoDB에 저장
    team = TeamData.create_new_entry(new_team_id, name, placement)

    logger.info(f"{name} 팀({placement}위)이 추가되었습니다.")
    return True

# 팀 수정
def update_team(name: str, placement: int):
    team_data: TeamData
    try:
        team_data = TeamData.load_from_db(name = name)
    except ValueError:
        logger.error(f"{name} 팀이 존재하지 않습니다.")
        return False
    try:
        team_data.placement = placement
        logger.info(f"{name} 팀의 순위를 {placement}위로 설정하였습니다.")
        return True
    except ValueError:
        logger.error(f"{name} 팀의 순위를 {placement}로 설정할 수 없습니다.")
        return False
