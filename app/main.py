import discord
from discord.ext import commands
import os
import re
import dotenv
import difflib

from server import server_thread

dotenv.load_dotenv()

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

# テキストチャンネル上でのコマンドは文頭「!」のものとする。intentsはさっき指定した通りのヤツだ
bot = commands.Bot(command_prefix="!", intents=intents)

# ---- 曖昧一致ロール検索関数 ----
def find_role_fuzzy(guild, role_name):
    role_names = [role.name for role in guild.roles]
    matches = difflib.get_close_matches(role_name, role_names, n=1, cutoff=0.6)
    if matches:
        return discord.utils.get(guild.roles, name=matches[0])
    return None

 # botのTOKENを環境変数から取得する。(Koeyb側で設定)
TOKEN = os.environ.get("TOKEN")

# サーバーごとの設定
SETTINGS = {
    348814267782397964: {  # 大学東方のアレのID
        "intro_channel": 354625793844051970,  # 自己紹介チャンネルID
        "log_channel": 1406653580718379018,    # ログチャンネルID
        "guest_role": "Guest",
        "user_role": "user"
    },
    853160152647598100: {  # 魔導書の実験室のID
        "intro_channel": 1390572701462171658,
        "log_channel": 1390572992601526282,
        "guest_role": "guest",
        "user_role": "user"
    }
}

 # botを起動する
@bot.event
async def on_ready():
    print(f"[起動] Bot {bot.user} がログインしました")

def extract_circle_name(message: str):
    """所属サークル名を抽出"""
    for line in message.splitlines():
        if "所属" in line:
            parts = re.split(r"[:：]", line, maxsplit=1)
            # N_of_circle = len(parts.rsplit(r"[,、]", line,))
            if len(parts) > 1:
                return parts[1].strip()
    return None

def find_best_role(guild, target_name):
    """ロール名の曖昧一致検索"""
    role_names = [role.name for role in guild.roles]
    best_match = difflib.get_close_matches(target_name, role_names, n=1, cutoff=0.6)
    if best_match:
        return discord.utils.get(guild.roles, name=best_match[0])
    return None


@bot.event
async def on_message(message: discord.Message):
    # Bot自身のメッセージは無視
    if message.author.bot:
        return

    # ここでギルド情報を取る
    guild = message.guild
    settings = SETTINGS.get(guild.id)

    # 設定がなければ無視
    if not settings:
        return
    
    guild = message.guild
    if guild is None:
       return

    settings = SETTINGS.get(guild.id)
    if not settings:
        return  # 設定されていないサーバーは無視

    # 自己紹介チャンネル以外は無視
    if message.channel.id != settings["intro_channel"]:
        return

    log_channel = guild.get_channel(settings["log_channel"])

    # 「HN」が含まれる → guest外してuser付与
    if "HN" in message.content:
        user_role = discord.utils.get(guild.roles, name=settings["user_role"])
        guest_role = discord.utils.get(guild.roles, name=settings["guest_role"])

        if user_role:
            await message.author.add_roles(user_role)
            if guest_role:
                await message.author.remove_roles(guest_role)
            if log_channel:
                await log_channel.send(f"{message.author.display_name} に {user_role.name} ロールを付与しました！")

    # 「所属」が含まれる → サークルロール付与
    if "所属" in message.content:
        circle_name = extract_circle_name(message.content)
        if circle_name:
            role = find_best_role(guild, circle_name)
            if role:
                await message.author.add_roles(role)
                if log_channel:
                    await log_channel.send(f"{message.author.display_name} に {role.name} ロールを付与しました！")
            else:
                if log_channel:
                    await log_channel.send(f"{message.author.display_name} に所属ロールを付与できませんでした…")

    await bot.process_commands(message)

# Koyeb用 サーバー立ち上げ
server_thread()
# bot起動
bot.run(TOKEN)

