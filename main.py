import logging
import os
import discord 
from discord.ext import commands
from discord import app_commands
from sharing_codes import register_players, players_data

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 봇의 프리픽스 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# 각 Cog 파일 로드
async def load_cogs():
    await bot.load_extension("convenience")  # convenience.py 파일 로드
    await bot.load_extension("team_management")  # team_management.py 파일 로드
    await bot.load_extension("gold")  # gold.py 파일 로드
    await bot.load_extension("ranking")  # ranking.py 파일 로드
    await bot.load_extension("admin")  # admin.py 파일 로드

# 봇이 준비되었을 때 실행되는 이벤트
@bot.event
async def on_ready():
    logger.info(f'봇이 실행되었습니다: {bot.user}')  # 봇 시작 로그
    # 봇 시작 시 선수 데이터 초기화
    register_players()
    logger.debug(f'{players_data}')
    await load_cogs()  # Cog 로드
    await bot.tree.sync()  # 슬래시 커맨드 동기화
    logger.info("슬래시 커맨드 동기화 완료.")  # 커맨드 동기화 로그
    print(f'Logged in as {bot.user}!')

# 미등록 명령어에 대한 경고 메시지 처리
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # 봇의 메시지는 무시

    ctx = await bot.get_context(message)
    if ctx.command is None and message.content.startswith(bot.command_prefix):
        await message.channel.send("올바르지 않은 명령어입니다. '/명령어'를 입력하여 사용 가능한 명령어를 확인해 주세요.")

    await bot.process_commands(message)  # 명령어 처리 추가


token = ''

with open('token.txt', 'r') as token_file:
    token = token_file.read().rstrip()

bot.run(token)