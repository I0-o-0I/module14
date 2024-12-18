from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import  *
from crud_functions14_5 import *
import asyncio



api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())
kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = 'Информация'),
                                    KeyboardButton(text = 'Рассчитать'),
                                    KeyboardButton(text = 'Купить')],
                                    [KeyboardButton(text = 'Регистрация')]],
                         resize_keyboard=True)
inkb = InlineKeyboardMarkup()
b = InlineKeyboardButton(text = 'Рассчитать норму калорий', callback_data = 'calories')
b2 = InlineKeyboardButton(text = 'Формулы расчёта', callback_data = 'formulas')
inkb.add(b)
inkb.add(b2)
inkb2=InlineKeyboardMarkup()
p1 = InlineKeyboardButton(text='Product1', callback_data='product_buying')
p2 = InlineKeyboardButton(text='Product2', callback_data='product_buying')
p3 = InlineKeyboardButton(text='Product3', callback_data='product_buying')
p4 = InlineKeyboardButton(text='Product4', callback_data='product_buying')
inkb2.add(p1)
inkb2.add(p2)
inkb2.add(p3)
inkb2.add(p4)

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup = kb)

@dp.message_handler(text = 'Информация')
async def info(message):
    await message.answer('Информация о боте')

@dp.message_handler(text = 'Купить')
async def get_buying_list(message):
    products = get_all_products()
    for number in products:

        await message.answer(f'Название: {number[1]} | Описание: {number[2]} | Цена: {number[3]}')
        with open(f'files/{number[0]}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup = inkb2)

@dp.message_handler(text = 'Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup = inkb)

@dp.callback_query_handler(text = 'product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()

@dp.callback_query_handler(text = 'formulas')
async def formula(call):
    await call.message.answer('10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()

@dp.callback_query_handler(text = 'calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age = int(message.text))
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth = int(message.text))
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight = int(message.text))
    data = await state.get_data()

    a = 10 * data['weight'] + 6.25 + data['growth'] - 5 * data['age'] - 161
    await message.answer(f'Ваша норма калорий: {a}')
    await state.finish()

@dp.message_handler(text = 'Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if is_included(message.text):
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()
    else:
        await state.update_data(username = message.text)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email = message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age = int(message.text))
    await state.update_data(balance=1000)
    data = await state.get_data()
    add_users(data['username'], data['email'], data['age'], data['balance'])
    await message.answer("Регистрация прошла успешно")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)