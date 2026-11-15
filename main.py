import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from aiogram import Bot, Dispatcher
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

app = FastAPI()

# Статика (если понадобится)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

BOT_TOKEN = os.getenv("9187781523:AAGlo3rrSECl8wurPG_XmxTO-GepWZnLuqc")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")

bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if WEBAPP_URL:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🐱 Открыть тамагочи", web_app=WebAppInfo(url=WEBAPP_URL))]
        ])
        await message.answer("Привет! Открой тамагочи:", reply_markup=kb)
    else:
        await message.answer("Привет! URL Mini App не настроен.")

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
async def health():
    return {"status": "ok"}

async def start_bot():
    if bot:
        await dp.start_polling(bot)

@app.on_event("startup")
async def startup():
    asyncio.create_task(start_bot())
