import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import random
import os
TOKEN = os.environ.get("TOKEN")
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─────────────────────────────────────────
# 💬 자동응답 데이터
# ─────────────────────────────────────────
responses = {
    ("안녕", "ㅎㅇ", "하이", "헬로"):                      "안녕하세요",
    ("심심",):                                              "저도 친구가 없어서 심심해요",
    ("사랑해", "좋아해"):                                   "네...",
    ("몇 살", "몇살", "나이"):                              "7살이에요",
    ("아키토",):                                            "팬케이크...?",
    ("쿼쥐",):                                              "무서워요",
    ("잘 자", "잘자", "굿나잇", "ㅈㅈ"):                   "안녕히 주무세요",
    ("염소",):                                              "앗 밟혔다",
    ("처녀",):                                              "앗 밟았다",
    ("씨발", "시발", "ㅗ", "새끼"):                        "욕하지 마세요...",
    ("루이츠카",):                               "🎈🌟",
    ("루이네네", "루이에무", "츠카네네", "츠카에무", "츠카루이"):       "좆같은소리하지마",
    ("네네에무",):                                          "🤖🍬",
    ("츠카사",):                                            "🌟",
    ("에무",):                                              "🍬",
    ("네네",):                                              "🤖",
    ("토키슌이치",):                                              "아...빠...?",
    ("린타로",):                                              "어디서 들어본 목소리에요",
    ("오리너구리", "오구리"):                                              "🥰",

}

DEFAULT_RESPONSE = "잘 모르겠어요..."
MENTION_RESPONSES = ["??"]

# ─────────────────────────────────────────
# 💬 자동응답 이벤트
# ─────────────────────────────────────────
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    # 루이야 or 멘션 없으면 무시
    triggered = bot.user.mentioned_in(message) and not message.mention_everyone
    if not triggered and not content.startswith("루이야"):
        await bot.process_commands(message)
        return

    # 멘션만 했을 때 (루이야 없이)
    if triggered and "루이야" not in content:
        await message.channel.send(random.choice(MENTION_RESPONSES))
        await bot.process_commands(message)
        return

    # 루이야 뒤의 내용만 추출
    content = content.replace("루이야", "", 1).strip()

    # 루이야만 단독으로 쳤을 때
    if content == "":
        await message.channel.send("네")
        await bot.process_commands(message)
        return

    # 🎲 주사위
    if content == "주사위":
        result = random.randint(1, 6)
        await message.channel.send(f"🎲 {result}!")
        await bot.process_commands(message)
        return

    # ✂️ 가위바위보
    if content in ("가위", "바위", "보"):
        bot_choice = random.choice(["가위", "바위", "보"])
        wins = {"가위": "보", "바위": "가위", "보": "바위"}
        if content == bot_choice:
            result = "비겼어요!"
        elif wins[content] == bot_choice:
            result = "졌어요ㅠ"
        else:
            result = "이겼어요!"
        await message.channel.send(f"저는 {bot_choice}! {result}")
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

