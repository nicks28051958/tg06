import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
import random
import sqlite3
import aiohttp
import logging
import os
import requests
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

button_registr = KeyboardButton(text="Регистрация в телеграм боте")
button_exchange_rates = KeyboardButton(text="Курс валют")
button_finances = KeyboardButton(text="Личные финансы")
button_tips = KeyboardButton(text="Советы по экономии")
button_limit = KeyboardButton(text="Месячный доход")


keyboard = ReplyKeyboardMarkup(keyboard=[
    [button_registr, button_exchange_rates],
    [button_tips, button_finances, button_limit]
])

keyboard = ReplyKeyboardMarkup(keyboard=[
    [button_registr, button_exchange_rates],
    [button_tips, button_finances, button_limit]
    ], resize_keyboard=True)

db_path = 'F:\\STUDENT_PYTHON\\TG06\\tg06\\user.db'
conn = sqlite3.connect(db_path)
print("Database created at:", os.path.abspath(db_path))
cursor = conn.cursor()



cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    name TEXT,
    category1 TEXT,
    category2 TEXT,
    category3 TEXT,
    expenses1 REAL,
    expenses2 REAL,
    expenses3 REAL
    )
''')
conn.commit()


class FinancesForm(StatesGroup):
    category1 = State()
    expenses1 = State()
    category2 = State()
    expenses2 = State()
    category3 = State()
    expenses3 = State()


@dp.message(Command('start'))
async def send_start(message: Message):
    await message.answer("Привет! Я ваш личный финансовый помощник. Выберите одну из опций в меню:", reply_markup=keyboard)

@dp.message(F.text == "Регистрация в телеграм боте")
async def registration(message: Message):
   telegram_id = message.from_user.id
   name = message.from_user.full_name
   cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
   user = cursor.fetchone()
   if user:
       await message.answer("Вы уже зарегистрированы!")
   else:
       cursor.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
       conn.commit()
       await message.answer("Вы успешно зарегистрированы!")


@dp.message(F.text == "Курс валют")
async def exchange_rates(message: Message):
    url = "https://v6.exchangerate-api.com/v6/b2e6bdd932ff26c7f07e9258/latest/USD"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            await message.answer("Не удалось получить данные о курсе валют!")
            return
        usd_to_rub = data['conversion_rates']['RUB']
        eur_to_usd = data['conversion_rates']['EUR']
        gbp_to_usd = data['conversion_rates']['GBP']
        cny_to_usd = data['conversion_rates']['CNY']



        euro_to_rub = usd_to_rub/eur_to_usd
        gbp_to_rub = usd_to_rub/gbp_to_usd
        cny_to_rub = usd_to_rub/cny_to_usd

        await message.answer(f"1 Доллар США - {usd_to_rub:.2f}  RUB\n"
                             f"1 Евро - {euro_to_rub:.2f} RUB\n"
                             f"1 Фунт стерлингов - {gbp_to_rub:.2f} RUB\n"
                             f"1 Китайский юань - {cny_to_rub:.2f}  RUB")


    except:
        await message.answer("Произошла ошибка")

@dp.message(F.text == "Советы по экономии")
async def send_tips(message: Message):
    tips = [
        "Совет 1: Ведите бюджет и следите за своими расходами.",
        "Совет 2: Откладывайте часть доходов на сбережения.",
        "Совет 3: Покупайте товары по скидкам и распродажам.",
        "Совет 4: Сравнивайте цены перед покупкой.",
        "Совет 5: Избегайте долгов и кредитов на необязательные покупки.",
        "Совет 6: Замените платные развлечения на бесплатные или бюджетные варианты."
        ]
    tip = random.choice(tips)
    await message.answer(tip)

@dp.message(F.text == "Личные финансы")
async def finances(message: Message, state: FSMContext):
   await state.set_state(FinancesForm.category1)
   await message.reply("Введите первую категорию расходов:")

@dp.message(FinancesForm.category1)
async def finances(message: Message, state: FSMContext):
   await state.update_data(category1 = message.text)
   await state.set_state(FinancesForm.expenses1)
   await message.reply("Введите расходы для категории 1:")

@dp.message(FinancesForm.expenses1)
async def finances(message: Message, state: FSMContext):
   await state.update_data(expenses1 = float(message.text))
   await state.set_state(FinancesForm.category2)
   await message.reply("Введите вторую категорию расходов:")

@dp.message(FinancesForm.category2)
async def finances(message: Message, state: FSMContext):
   await state.update_data(category2 = message.text)
   await state.set_state(FinancesForm.expenses2)
   await message.reply("Введите расходы для категории 2:")

@dp.message(FinancesForm.expenses2)
async def finances(message: Message, state: FSMContext):
   await state.update_data(expenses2 = float(message.text))
   await state.set_state(FinancesForm.category3)
   await message.reply("Введите третью категорию расходов:")

@dp.message(FinancesForm.category3)
async def finances(message: Message, state: FSMContext):
   await state.update_data(category3 = message.text)
   await state.set_state(FinancesForm.expenses3)
   await message.reply("Введите расходы для категории 3:")

@dp.message(FinancesForm.expenses3)
async def finances(message: Message, state: FSMContext):
   data = await state.get_data()
   telegarm_id = message.from_user.id
   cursor.execute('''UPDATE users SET category1 = ?, expenses1 = ?, category2 = ?, expenses2 = ?, category3 = ?, expenses3 = ? WHERE telegram_id = ?''',
                  (data['category1'], data['expenses1'], data['category2'], data['expenses2'], data['category3'], float(message.text), telegarm_id))
   conn.commit()
   await state.clear()

   await message.answer("Категории и расходы сохранены!")


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())