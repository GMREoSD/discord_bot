import discord
from discord.ext import commands
import os
import dotenv

from server import server_thread

dotenv.load_dotenv()

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

# テキストチャンネル上でのコマンドは文頭「!」のものとする。intentsはさっき指定した通りのヤツだ
bot = commands.Bot(command_prefix="!", intents=intents)

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
    if message.author.bot:
        return

    if message.channel.id != SELF_INTRO_CHANNEL_ID:
        return

    guild = message.guild
    member = message.author
    content = message.content
    log_channel = guild.get_channel(LOG_CHANNEL_ID)

    # --- ユーザーロール付与 ---
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
    assigned = False
    if "所属" in content:
        for line in content.splitlines():
            if "所属" in line:
                # 「：」または「:」で分割
                if "：" in line:
                    parts = line.split("：", 1)
                elif ":" in line:
                    parts = line.split(":", 1)
                else:
                    continue

                if len(parts) == 2:
                    raw_name = parts[1].strip()
                    if not raw_name:
                        continue
                    role = discord.utils.get(guild.roles, name=raw_name)
                    if role:
                        await member.add_roles(role)
                        assigned = True
                        if log_channel:
                            await log_channel.send(f"✅ {member.display_name} に `{role.name}` ロールを付与しました！")
                        break
        if not assigned and log_channel:
            await log_channel.send(f"⚠️ {member.display_name} に所属ロールを付与できませんでした")

    await bot.process_commands(message)

# Koyeb用 サーバー立ち上げ
server_thread()
# bot起動
bot.run(TOKEN)

