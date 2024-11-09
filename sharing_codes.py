import logging

logger = logging.getLogger(__name__)

# 데이터 파일 경로
DATA_FILE = "players_data.json"

# 초기 예산 설정
STARTING_BUDGET = 150

# 출석 골드 설정
DAILY_REWARD = 5

# 티어에 따른 가치 정의
TIER_VALUES = {
    "S": 50,
    "A": 40,
    "B": 30,
    "C": 20,
    "D": 10,
}

# 선수 등록 활성화 플래그
is_registration_active = True
is_sale_active = True

# FT잡담 채널 ID: 1302961629562011750 
# FT명령어 채널 ID: 1302944526750453820
# 테섭 채널 ID: 1304615715139223585

ALLOWED_CHANNEL_ID = [1304615715139223585] # 명령어 채널
COMMUNITY_CHANEL_ID = [1304613112439111680] # 잡담+명령어 채널