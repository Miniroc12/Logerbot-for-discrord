import discord
import sqlite3
from datetime import datetime
from tokens import DISCORD_TOKEN

TOKEN = DISCORD_TOKEN

intents = discord.Intents.default()
intents.messages = True  # Отслеживание сообщений
intents.voice_states = True  # Отслеживание голосовых каналов
intents.members = True  # Отслеживание входа/выхода

bot = discord.Client(intents=intents)

# Подключение к базе данных
conn = sqlite3.connect("logs.db")
cursor = conn.cursor()

# Создание таблицы (если нет)
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    event TEXT,
    channel TEXT,
    timestamp TEXT
)
""")
conn.commit()

@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")

@bot.event
async def on_member_join(member):
    log_event(member.id, member.name, "join", "Server")

@bot.event
async def on_member_remove(member):
    log_event(member.id, member.name, "leave", "Server")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    log_event(message.author.id, message.author.name, "message", message.channel.name)

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        log_event(member.id, member.name, "voice_join", after.channel.name)
    elif before.channel is not None and after.channel is None:
        log_event(member.id, member.name, "voice_leave", before.channel.name)

def log_event(user_id, username, event, channel):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (user_id, username, event, channel, timestamp) VALUES (?, ?, ?, ?, ?)", 
                   (user_id, username, event, channel, timestamp))
    conn.commit()

bot.run(TOKEN)
