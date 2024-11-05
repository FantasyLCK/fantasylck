import logging
import os
import discord 
from discord.ext import commands
from team_management import 선수등록, 선수판매, 내팀
from convenience import 선수목록, 명령어, 관리자, 육구놀이룰
from gold import 육구놀이, 출석
from admin import 선수추가, 선수삭제, 선수수정, on, off
from ranking import 맞다이, 랭킹

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

# 봇의 프리픽스 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 봇이 준비되었을 때 실행되는 이벤트
@bot.event
async def on_ready():
    logger.info(f'봇이 실행되었습니다: {bot.user}')

# 미등록 명령어에 대한 경고 메시지 처리
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # 봇의 메시지는 무시

    ctx = await bot.get_context(message)
    if ctx.command is None and message.content.startswith(bot.command_prefix):
        await message.channel.send("올바르지 않은 명령어입니다. '!명령어'를 입력하여 사용 가능한 명령어를 확인해 주세요.")
    
    await bot.process_commands(message)


# 명령어 등록
bot.add_command(선수등록)
bot.add_command(선수판매)

bot.add_command(내팀)
bot.add_command(선수목록)
bot.add_command(명령어)
bot.add_command(관리자)
bot.add_command(육구놀이룰)

bot.add_command(육구놀이)
bot.add_command(출석)

bot.add_command(선수추가)
bot.add_command(선수수정)
bot.add_command(선수삭제)

bot.add_command(on)
bot.add_command(off)

bot.add_command(맞다이)
bot.add_command(랭킹)

TOKEN = os.getenv('MTMwMTQ0NTMwNzg5MTk3NDE4NQ.GC0AfA.v42uQ7fqNk9Q0p0T29jaHyhCpg18MupbFP1D9A')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN 환경 변수가 설정되지 않았습니다.")

client = discord.Client()
client.run(TOKEN)