from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.template.defaultfilters import title
import crud_functions
import asyncio
from crud_functions import *

#Создаем подключение к боту
api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

#Создаем основную не инлайн клавиатуру
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text="Рассчитать")
button2 = KeyboardButton(text="Информация")
button3 = KeyboardButton(text="Купить")
button4 = KeyboardButton(text="Регистрация")
kb.add(button,button2)
kb.add(button3, button4)

#Создаем инлайн клавиатуру для расчета нормы калорий либо
# вывода формулы расчета
ikb = InlineKeyboardMarkup()
button = InlineKeyboardButton(text='Рассчитать норму калорий',
                              callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчёта',
                              callback_data='formulas')
ikb.add(button)
ikb.add(button2)

#Создаем инлайн клавиатуру для покупки продукции
ikb_buy = InlineKeyboardMarkup()
buy_button = InlineKeyboardButton(text='Продукт1',
                              callback_data='product_buying')
buy_button2 = InlineKeyboardButton(text='Продукт2',
                              callback_data='product_buying')
buy_button3 = InlineKeyboardButton(text='Продукт3',
                              callback_data='product_buying')
buy_button4 = InlineKeyboardButton(text='Продукт4',
                              callback_data='product_buying')
ikb_buy.add(buy_button, buy_button2, buy_button3, buy_button4)

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Info')],
        [
            KeyboardButton(text='shop'),
            KeyboardButton(text='donate')
        ]
    ], resize_keyboard=True
)

#Создаем обработчик для кнопки "Рассчитать" основной клавиатуры
@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=ikb)

# Создаем обработчик для кнопки "Купить" основной клавиатуры
@dp.message_handler(text='Купить')
async def get_buying_list(message):
    titles, descriptions, prices = get_all_products()
    for number in range(0, 4):
        await message.answer(f'Название: {titles[number]} | Описание: {descriptions[number]}'
                             f' | Цена: {prices[number]}')
        with open(f'files/{number}.jpg', "rb") as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup=ikb_buy)

#Создаем обработчик кнопок инлайн клавиатуры для покупки продукции
@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')

#Создаем обработчик для кнопки "Формулы расчета" инлайн клавиатуры
# для расчета нормы калорий либо вывода формулы расчета
@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Формула рассчета для мужчин: '
                              '10 х вес (кг) + 6,25 x рост (см)'
                              ' – 5 х возраст (г) + 5')
    await call.message.answer('Формула рассчета для женщин: '
                              '10 x вес (кг) + 6,25 x рост (см)'
                              ' – 5 x возраст (г) – 161')
    await call.answer()

#Создаем класс, описывающий исходные данные для расчета нормы калорий
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

#Создаем класс состояний RegistrationState
class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()


#Создаем цепочку изменений состояний RegistrationState
@dp.message_handler(text='Регистрация')
async def sing_up(message, state):
    await message.answer(f'Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if not is_included(message.text):
        await state.update_data(username=message.text)
        await message.answer(f'Введите свой email:')
        await RegistrationState.email.set()
    else:
        await message.answer(f'Пользователь существует, введите другое имя')
        await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer(f'Введите свой возраст:')
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    add_user(data.get('username'), data.get('email'), data.get('age'))
    print('username: ', data.get('username'))
    print('email: ', data.get('email'))
    print('age: ', data.get('age'))
    await message.answer(f'Регистрация прошла успешно')
    await state.finish()
    return

#Создаем обработчики для кнопки "Рассчитать норму калорий" инлайн клавиатуры
# для расчета нормы калорий либо вывода формулы расчета
@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer(f'Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer(f'Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def fsm_handler(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    try:
        age = float(data['age'])
        weight = float(data['weight'])
        growth = float(data['growth'])
    except:
        await message.answer(f'Не могу конвертировать введенные значения в числа.')
        await state.finish()
        return

    # Упрощенный вариант формулы Миффлина-Сан Жеора:
    # для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5
    calories_man = 10 * weight + 6.25 * growth - 5 * age + 5
    # для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161
    calories_wom = 10 * weight + 6.25 * growth - 5 * age - 161
    await message.answer(f'Суточная норма калорий для мужчины: {calories_man} ккал')
    await message.answer(f'Суточная норма калорий для женщины: {calories_wom} ккал')
    await state.finish()
    return

#Создаем обработчик команды /start
@dp.message_handler(commands='start')
async def start_message(message):
    await message.answer('Привет! Я бот помогающий Вашему здоровью.', reply_markup=kb)



#Создаем обработчик, приветствующий пользователя и указывающий на необходимость
#ввода команды /start для запуска бота
@dp.message_handler()
async def all_message(message):
    await message.answer('Привет!')
    await message.answer('Введите команду /start, чтобы начать общение.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    