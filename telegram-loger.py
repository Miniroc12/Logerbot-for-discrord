import re
import sqlite3
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from tokens import TELEGRAM_TOKEN

TOKEN = TELEGRAM_TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp["bot"] = bot

#  получения логов из базы
def get_logs(event_type=None, date=None):
    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()

    query = "SELECT username, event, channel, timestamp FROM logs"
    params = []
    conditions = []

    if event_type:
        conditions.append("event = ?")
        params.append(event_type)
    if date:
        conditions.append("DATE(timestamp) = ?")
        params.append(date)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id DESC LIMIT 20"

    cursor.execute(query, params)
    logs = cursor.fetchall()
    conn.close()
    return logs

# Главное меню
def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎙️ Вход в голосовой канал", callback_data="log_voice_join")],
            [InlineKeyboardButton(text="📤 Выход из голосового канала", callback_data="log_voice_leave")],
            [InlineKeyboardButton(text="📝 Отправленные сообщения", callback_data="log_message")],
            [InlineKeyboardButton(text="👥 Присоединение пользователей", callback_data="log_user_join")],
            [InlineKeyboardButton(text="📋 Все логи", callback_data="log_all")],
        ]
    )

#  Бургер-меню 
menu_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Меню")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def show_menu(message: types.Message):
    await message.answer("Выберите тип логов:", reply_markup=main_menu())
    await message.answer("📌 Нажимайте «Меню», чтобы открыть главное меню в любой момент!", reply_markup=menu_button)

@dp.message(lambda message: message.text == "Меню")
async def burger_menu(message: types.Message):
    await message.answer("Выберите тип логов:", reply_markup=main_menu())

#  Функция форматирования логов
def format_log(log):
    username, event, channel, timestamp = log
    event_messages = {
        "voice_join": f"🎙️ {username} зашел в голосовой канал «{channel}»",
        "voice_leave": f"📤 {username} вышел из голосового канала «{channel}»",
        "message": f"💬 {username} отправил сообщение в «{channel}»",
        "join": f"👥 {username} присоединился к серверу",
        "leave": f"👥 {username} покинул сервер"
    }
    return f"🕒 {timestamp}\n{event_messages.get(event, 'Неизвестное событие')}"

#  Обработчик логов
@dp.callback_query(lambda call: call.data.startswith("log_") and call.data != "log_search_by_date")
async def send_logs_by_type(call: types.CallbackQuery):
    event_map = {
        "log_voice_join": "voice_join",
        "log_voice_leave": "voice_leave",
        "log_message": "message",
        "log_user_join": "join",
        "log_user_leave": "leave",
        "log_all": None  # Все логи
    }

    event_type = event_map.get(call.data)
    logs = get_logs(event_type=event_type)

    if not logs:
        await call.message.edit_text("❌ Логи пусты.", reply_markup=main_menu())
        return

    text = "\n\n".join([format_log(log) for log in logs])
    await call.message.edit_text(f"📋 Логи:\n{text}", reply_markup=main_menu())


# 📌 Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
