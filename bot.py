import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import random
import os
import asyncio
import pytz
from datetime import datetime

TOKEN = os.environ.get("TOKEN")
KST = pytz.timezone('Asia/Seoul')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─────────────────────────────────────────
# 💬 자동응답 데이터
# ─────────────────────────────────────────
responses = {
    ("루이네네", "루이에무", "츠카네네", "츠카에무", "츠카루이"):  "좆같은소리하지마",
    ("네네에무",):                                               "🤖🍬",
    ("루이츠카",):                                               "🎈🌟",
    ("안녕", "ㅎㅇ", "하이", "헬로"):                           "안녕하세요",
    ("심심",):                                                   "저도 친구가 없어서 심심해요",
    ("사랑해", "좋아해"):                                        "네...",
    ("츠카사",):                                                 "🌟",
    ("에무",):                                                   "🍬",
    ("네네",):                                                   "🤖",
    ("몇 살", "몇살", "나이"):                                   "7살이에요",
    ("아키토",):                                                 "팬케이크...?",
    ("쿼쥐",):                                                   "무서워요",
    ("잘 자", "잘자", "굿나잇", "ㅈㅈ"):                        "안녕히 주무세요",
    ("염소",):                                                   "앗 밟혔다",
    ("처녀",):                                                   "앗 밟았다",
    ("씨발", "시발", "ㅗ", "새끼"):                             "욕하지 마세요...",
    ("토키슌이치",):                                             "아...빠...?",
    ("린타로",):                                                 "어디서 들어본 목소리에요",
    ("오리너구리", "오구리"):                                    "🥰",
    ("자폭",):                                                   "1107",
    ("귀여워",):                                                 "아... 그쪽 취향...",
    ("미스터리",):                                                 "수사반",
    ("세카이데",):                                                 "이치방 오히메사마",
    ("죽어",):                                                 "그건 츠카사군의 역할이래요",
    ("미쿠",):                                                 "미쿠하게 해줄게",
    ("세레아스",):                                                 "아... 그건 좀...",
    ("다이츠키",):                                                 "기분이 좀 안 좋네요",
    ("일어나",):                                                 "왜 명령을 하시는거죠?",
    ("개",):                                                 "으르르르르",
    ("빵",):                                                 "나는 쓰러지지 않는다",
}

DEFAULT_RESPONSE = "잘 모르겠어요..."
MENTION_RESPONSES = ["??"]

# ─────────────────────────────────────────
# ⏰ 알림 기능
# ─────────────────────────────────────────
async def send_reminder(channel, user, memo, wait_seconds):
    await asyncio.sleep(wait_seconds)
    await channel.send(f"{user.mention} ⏰ {memo}")

# ─────────────────────────────────────────
# 💬 자동응답 이벤트
# ─────────────────────────────────────────
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    triggered = bot.user.mentioned_in(message) and not message.mention_everyone
    if not triggered and not content.startswith("루이야"):
        await bot.process_commands(message)
        return

    if triggered and "루이야" not in content:
        await message.channel.send(random.choice(MENTION_RESPONSES))
        await bot.process_commands(message)
        return

    content = content.replace("루이야", "", 1).strip()

    if content == "":
        await message.channel.send("네")
        await bot.process_commands(message)
        return

    # ⏰ 알림
    if content.startswith("알림 "):
        parts = content[3:].strip().split(" ", 1)
        try:
            time_str = parts[0]
            memo = parts[1] if len(parts) > 1 else "알림!"
            now = datetime.now(KST)
            hour, minute = map(int, time_str.split(":"))
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            wait = (target - now).total_seconds()
            if wait <= 0:
                await message.channel.send("이미 지난 시간이에요...")
            else:
                await message.channel.send(f"⏰ {time_str}에 알려드릴게요! ({int(wait//60)}분 후)")
                asyncio.create_task(send_reminder(message.channel, message.author, memo, wait))
        except:
            await message.channel.send("이렇게 써줘요! `루이야 알림 18:30 숙제하기`")
        await bot.process_commands(message)
        return

    # 🐶 짖어
    if content == "짖어":
        await message.channel.send(file=discord.File("voice_card_ev_shuffle_44_16_2b_55_16.mp3"))
        await bot.process_commands(message)
        return
    
    # 🎲 주사위
    if content == "주사위":
        result = random.randint(1, 6)
        await message.channel.send(f"🎲 {result}")
        await bot.process_commands(message)
        return

    # ✂️ 가위바위보
    if content in ("가위", "바위", "보"):
        bot_choice = random.choice(["가위", "바위", "보"])
        wins = {"가위": "보", "바위": "가위", "보": "바위"}
        if content == bot_choice:
            result = "다시"
        elif wins[content] == bot_choice:
            result = "지는 게 이기는 거에요"
        else:
            result = "이겼다"
        await message.channel.send(f"{bot_choice}! {result}")
        await bot.process_commands(message)
        return

    # 노래 검색
    if content.startswith("노래 "):
        query = content[3:].strip()
        await message.channel.send("🔍 찾는 중...")
        with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if info and 'entries' in info and info['entries']:
                video = info['entries'][0]
                url = f"https://www.youtube.com/watch?v={video['id']}"
                title = video['title']
                await message.channel.send(f"🎵 **{title}**\n{url}")
            else:
                await message.channel.send("찾지 못했어요...")
        await bot.process_commands(message)
        return

    # 키워드 매칭
    matched = False
    for keywords, reply in responses.items():
        if any(kw in content for kw in keywords):
            await message.channel.send(reply)
            matched = True
            break

    if not matched:
        await message.channel.send(DEFAULT_RESPONSE)

    await bot.process_commands(message)

# ─────────────────────────────────────────
# ✅ 봇 준비
# ─────────────────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} 로그인 완료!")

# ─────────────────────────────────────────
# ⚡ 슬래시 커맨드
# ─────────────────────────────────────────
@bot.tree.command(name="핑", description="봇 응답속도 확인")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 퐁! `{latency}ms`")

bot.run(TOKEN)










