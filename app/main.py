import discord
from discord.ext import commands
import os
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

# === 設定項目 ===
TOKEN = os.environ.get("TOKEN")
SELF_INTRO_CHANNEL_ID = 1390572701462171658
LOG_CHANNEL_ID = 1390572992601526282
GUEST_ROLE_NAME = "guest"
USER_ROLE_NAME = "user"

@bot.event
async def on_ready():
    print(f"[起動] Bot {bot.user} がログインしました")

@bot.event
async def on_message(message: discord.Message):
    # Bot自身のメッセージは無視
    if message.author.bot:
        return

    # 自己紹介チャンネル以外は無視
    if message.channel.id != SELF_INTRO_CHANNEL_ID:
        return

    guild = message.guild
    member = message.author
    content = message.content
    log_channel = guild.get_channel(LOG_CHANNEL_ID)

    # --- userロール付与 ---
    if "HN" in content:
        guest_role = discord.utils.get(guild.roles, name=GUEST_ROLE_NAME)
        user_role = discord.utils.get(guild.roles, name=USER_ROLE_NAME)

        if guest_role in member.roles:
            await member.remove_roles(guest_role)

        if user_role and user_role not in member.roles:
            await member.add_roles(user_role)
            if log_channel:
                await log_channel.send(f"✅ {member.display_name} に `{USER_ROLE_NAME}` ロールを付与しました！")

    # --- 所属ロール付与 ---
    if "所属" in message.content:
        for line in message.content.splitlines():
            if "所属" in line:
                # 「所属」行から : または ： の後の文字を取り出す
                if ":" in line:
                    role_name = line.split(":", 1)[1].strip()
                elif "：" in line:
                    role_name = line.split("：", 1)[1].strip()
                else:
                    role_name = None

                if role_name:
                    role = find_role_fuzzy(message.guild, role_name)
                    if role:
                        await message.author.add_roles(role)
                        await log_channel.send(f"{message.author.name} に {role.name} ロールを付与しました！")
                    else:
                        await log_channel.send(f"{message.author.name} に所属ロールを付与できませんでした。")

    await bot.process_commands(message)

# Koyeb用 サーバー立ち上げ
server_thread()
# bot起動
bot.run(TOKEN)

