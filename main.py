import os
import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton,
    PreCheckoutQuery, LabeledPrice
)
from aiogram.filters import Command

app = FastAPI()
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

BOT_TOKEN = os.getenv("9187781523:AAGlo3rrSECl8wurPG_XmxTO-GepWZnLuqc")
WEBAPP_URL = os.getenv("web-production-c02fbcbb.up.railway.app")

bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
dp = Dispatcher()

# Временное хранилище инвентаря (в реале нужно использовать БД)
user_inventory = {}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    if WEBAPP_URL:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🐱 Открыть тамагочи", web_app=WebAppInfo(url=WEBAPP_URL))]
        ])
        await message.answer("Привет! Открой тамагочи:", reply_markup=kb)
    else:
        await message.answer("Привет! URL Mini App не настроен.")

@dp.message(F.web_app_data)
async def web_app_data_handler(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "buy_stars":
            item = data.get("item")
            price = int(data.get("price"))
            
            await bot.send_invoice(
                chat_id=message.chat.id,
                title=f"Покупка: {item}",
                description=f"Аксессуар/Услуга {item}.",
                payload=f"item_{item}",
                provider_token="",
                currency="XTR",
                prices=[LabeledPrice(label=item, amount=price)]
            )
    except Exception as e:
        print(f"Ошибка данных: {e}")

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    item = payload.replace("item_", "")
    
    # Сохраняем в инвентарь пользователя
    user_id = message.from_user.id
    if user_id not in user_inventory:
        user_inventory[user_id] = []
    user_inventory[user_id].append(item)

    # Отправляем уведомление с кнопкой заново открыть Mini App
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Посмотреть обновление", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    
    await message.answer(
        f"🎉 Успешно куплено: {item}!\nТеперь ваш питомец может это примерить!", 
        reply_markup=kb
    )

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
