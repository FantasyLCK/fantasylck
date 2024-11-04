import discord
from discord.ext import commands
from team_management import 선수등록, 선수판매, 내팀
from convenience import 선수목록, 명령어, 관리자, 육구놀이룰
from gold import 육구놀이, 출석
from admin import 선수추가, 선수삭제, 선수수정, on, off
from ranking import 맞다이, 랭킹

# 봇의 프리픽스 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 봇이 준비되었을 때 실행되는 이벤트
@bot.event
async def on_ready():
    print(f'봇이 실행되었습니다: {bot.user}')


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


# 메인 함수
MY_TOKEN = "MTMwMTQ0NTMwNzg5MTk3NDE4NQ.GrOpPe.LKIH4MdIWi5ZXZjD6gbVPVgqGNIxk7B4r9sPvk"
bot.run(MY_TOKEN)