import logging
import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler("fantasylck.log")
stream_handler = logging.StreamHandler()

stream_formatter = logging.Formatter("%(asctime)-15s %(levelname)-8s %(message)s")
file_formatter = logging.Formatter(
    "{'time':'%(asctime)s', 'name': '%(name)s', \
    'level': '%(levelname)s', 'message': '%(message)s'}"
)

file_handler.setFormatter(file_formatter)
stream_handler.setFormatter(stream_formatter)

logger.addHandler(file_handler)

# 봇의 프리픽스 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)


# 각 Cog 파일 로드
async def load_cogs():
    await bot.load_extension("convenience")  # convenience.py 파일 로드
    await bot.load_extension("team_management")  # team_management.py 파일 로드
    await bot.load_extension("attendence")  # attendendce.py 파일 로드
    await bot.load_extension("ranking")  # ranking.py 파일 로드
    await bot.load_extension("admin")  # admin.py 파일 로드


# 봇이 준비되었을 때 실행되는 이벤트
@bot.event
async def on_ready():
    logger.info(f"Bot is ready: {bot.user}")  # 봇 시작 로그
    await load_cogs()  # Cog 로드
    await bot.tree.sync()  # 슬래시 커맨드 동기화
    logger.info("Slach command tree synced.")  # 커맨드 동기화 로그
    logger.info(f"Logged in as {bot.user}!")


# 미등록 명령어에 대한 경고 메시지 처리
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # 봇의 메시지는 무시

    ctx = await bot.get_context(message)
    if ctx.command is None and message.content.startswith(bot.command_prefix):
        await message.channel.send(
            "올바르지 않은 명령어입니다. '/명령어'를 입력하여 사용 가능한 명령어를 확인해 주세요."
        )

    await bot.process_commands(message)  # 명령어 처리 추가


token = ""
with open("token.txt", "r") as token_file:
    token = token_file.read().rstrip()
bot.run(token)
