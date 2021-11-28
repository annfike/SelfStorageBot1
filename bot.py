import asyncio
import datetime
import logging
import os
import re
import json
from pprint import pprint

import aiogram.utils.markdown as fmt
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.message import ContentType
from dotenv import load_dotenv
import png

import emoji
import aiogram.utils.markdown as fmt
import time
from datetime import date, timedelta
import pyqrcode
from geopy.distance import geodesic as GD

loop = asyncio.get_event_loop()



logging.basicConfig(level=logging.INFO)
load_dotenv()
token = os.getenv("BOT_KEY")
PAYMENTS_PROVIDER_TOKEN = os.getenv("PAY_TOKEN")
user_data = {}
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)



class FsmAdmin(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    passport = State()
    born = State()

@dp.callback_query_handler(text='start')
@dp.message_handler(text='В начало')
@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)\

    keyboard.add(KeyboardButton('Отправить свою локацию 🗺️', request_location=True))
    keyboard.add(KeyboardButton('Выбрать руками 🤦'))

    if message.text == 'В начало':
        await message.answer("Рады видеть Вас снова! Начнем! \n"
                             "Пришлите мне, пожалуйста, повторно свою геолокацию, или выберете из списка! "
                             "И мы снова предложем ближайший склад",
                             reply_markup=keyboard)
    else:
        await message.answer("Привет! 🖐\n\n Я помогу вам арендовать личную ячейку для хранения вещей.\n"
                             "Пришлите мне, пожалуйста свою геолокацию или выберете из списка,"
                             " чтобы вы выбрали ближайший склад!",
                             reply_markup=keyboard)
    await bot.delete_message(message.from_user.id, message.message_id)


@dp.message_handler(text='Выбрать руками 🤦')
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        "метро Анино",
        "метро Китай-Город",
        "метро ВДНХ",
        "метро Митино",
        "метро Спартак",
        "метро Сокол",
    ]
    keyboard.add(*buttons)
    await message.answer('Выберите адрес склада:', reply_markup=keyboard)



@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Location):
    user_data['lat'] = message.location.latitude
    user_data['lon'] = message.location.longitude
    user_location = (user_data['lat'], user_data['lon'])
    location_anino = (55.581818, 37.594978)
    location_chinatown = (55.75634, 37.63002)
    location_vdnh = (55.82177, 37.64107)
    location_mitino = (55.84589, 37.35909)
    location_spartak = (55.8176765, 37.4345436)
    location_sokol = (55.80518, 37.51495)
    distance_anino = round(GD(user_location, location_anino).km)
    distance_chinatown = round(GD(user_location, location_chinatown).km)
    distance_vdnh = round(GD(user_location, location_vdnh).km)
    distance_mitino = round(GD(user_location, location_mitino).km)
    distance_spartak = round(GD(user_location, location_spartak).km)
    distance_sokol = round(GD(user_location, location_sokol).km)

    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    buttons = [
        f"метро Анино \n({distance_anino} км от вас) 😉",
        f"метро Китай-Город \n({distance_chinatown} км от вас)",
        f"метро ВДНХ \n({distance_vdnh} км от вас)",
        f"метро Митино \n({distance_mitino} км от вас)",
        f"метро Спартак \n({distance_spartak} км от вас)",
        f"метро Сокол \n({distance_sokol} км от вас)",
    ]
    keyboard.add(*buttons)
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer('Какой адрес вам подходит?', reply_markup=keyboard)


@dp.message_handler(text_contains="метро")
async def sklad_1_answer(message: types.Message):
    user_data['adress'] = message.text
  
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)

    buttons = [
        types.InlineKeyboardButton(text='сезонные вещи', callback_data='сезонные вещи'),
        types.InlineKeyboardButton(text='другое', callback_data='другое')
    ]
    keyboard.add(*buttons)
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer("Что хотите хранить?:", reply_markup=keyboard)
    await message.answer('💁‍♀️', reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(text='сезонные вещи')
async def send_msg(call: types.CallbackQuery):

    buttons = [
        types.InlineKeyboardButton(text='Лыжи', callback_data='Лыжи'),
        types.InlineKeyboardButton(text='Сноуборд', callback_data='Сноуборд'),
        types.InlineKeyboardButton(text='Велосипед', callback_data='Велосипед'),
        types.InlineKeyboardButton(text='Колеса', callback_data='Колеса'),
               ]

    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer("Выберите из списка:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text='Лыжи')
@dp.callback_query_handler(text='Сноуборд')
@dp.callback_query_handler(text='Велосипед')
@dp.callback_query_handler(text='Колеса')
async def seasonal_choose_quantity(call: types.CallbackQuery):
    user_data['item'] = call.data
    await call.message.answer(
        fmt.text(
            fmt.text(fmt.hunderline("Условия:\n\n")),
            fmt.text('1 лыжи - 100 р/неделя или 300 р/мес\n'),
            fmt.text('1 сноуборд - 100 р/неделя или 300 р/мес\n'),
            fmt.text('4 колеса - 200 р/мес\n'),
            fmt.text('1 велосипед - 150 р/ неделя или 400 р/мес\n'),
        ),
        reply_markup=types.ReplyKeyboardRemove()
    )
    buttons = [
        types.InlineKeyboardButton(
            text=f'{cell} шт', callback_data=f'{cell} шт') for cell in range(1, 11)
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=5, resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer("Укажите количество вещей для хранения.", reply_markup=keyboard)
    await call.answer()


@ dp.callback_query_handler(text_contains='шт')
async def seasonal_choose_period(call: types.CallbackQuery):
    user_data['quantity'] = call.data
    buttons = [
        types.InlineKeyboardButton(text='1 неделя', callback_data='1 неделя'),
        types.InlineKeyboardButton(text='2 недели', callback_data='2 недели'),
        types.InlineKeyboardButton(text='3 недели', callback_data='3 недели'),
        types.InlineKeyboardButton(text='1 месяц', callback_data='1 месяц'),
        types.InlineKeyboardButton(text='2 месяца', callback_data='2 месяца'),
        types.InlineKeyboardButton(text='3 месяца', callback_data='3 месяца'),
        types.InlineKeyboardButton(text='4 месяца', callback_data='4 месяца'),
        types.InlineKeyboardButton(text='5 месяцев', callback_data='5 месяцев'),
        types.InlineKeyboardButton(text='6 месяцев', callback_data='6 месяцев'),
               ]

    keyboard = types.InlineKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer("Выберите период хранения.", reply_markup=keyboard)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.answer()


@ dp.callback_query_handler(text='1 неделя')
@ dp.callback_query_handler(text='2 недели')
@ dp.callback_query_handler(text='3 недели')
@ dp.callback_query_handler(text='1 месяц')
@ dp.callback_query_handler(text='2 месяца')
@ dp.callback_query_handler(text='3 месяца')
@ dp.callback_query_handler(text='4 месяца')
@ dp.callback_query_handler(text='5 месяцев')
@ dp.callback_query_handler(text='6 месяцев')
async def seasonal_book(call: types.CallbackQuery):
    user_data['rent'] = call.data
    periods = {
            '1 неделя': 7,
            '2 недели': 14,
            '3 недели': 21,
            '1 месяц': 31,
            '2 месяца': 61,
            '3 месяца': 92,
            '4 месяца': 122,
            '5 месяцев': 153,
            '6 месяцев': 184,
            }
    prices = {
    'Лыжи': {
        '1 неделя': 100,
        '2 недели': 200,
        '3 недели': 300,
        '1 месяц': 300,
        '2 месяца': 600,
        '3 месяца': 900,
        '4 месяца': 1200,
        '5 месяцев': 1500,
        '6 месяцев': 1800,
        },
    'Велосипед': {
        '1 неделя': 150,
        '2 недели': 300,
        '3 недели': 450,
        '1 месяц': 400,
        '2 месяца': 800,
        '3 месяца': 1200,
        '4 месяца': 1600,
        '5 месяцев': 2000,
        '6 месяцев': 2400,
        },
    'Сноуборд': {
        '1 неделя': 100,
        '2 недели': 200,
        '3 недели': 300,
        '1 месяц': 300,
        '2 месяца': 600,
        '3 месяца': 900,
        '4 месяца': 1200,
        '5 месяцев': 1500,
        '6 месяцев': 1800,
        },
    'Колеса': {
        '1 месяц': 200,
        '2 месяца': 400,
        '3 месяца': 600,
        '4 месяца': 800,
        '5 месяцев': 1000,
        '6 месяцев': 1200,
        },
    }
    period = user_data['rent']
    period_days = periods[period]
    storage = user_data['adress']
    item = user_data['item']
    quantity = user_data['quantity']
    quantity = re.findall(r'\d+', quantity)[0]
   
    total_price = int(quantity) * prices[item][period]
    user_data['period_days'] = period_days
    user_data['total_price'] = total_price

    buttons = [
        types.InlineKeyboardButton(
            text="Забронировать", callback_data='Забронировать')
    ]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer(
        fmt.text(
            fmt.text(fmt.hunderline("Вы выбрали:")),
            fmt.text(f"\nЧто храним:   {item} "),
            fmt.text(f"\nСрок аренды:   {period} "),
            fmt.text(f"\nПо адресу:   {storage}"),
            fmt.text(f"\nСтоимость:   {total_price} рублей"), sep="\n"
        ), reply_markup=keyboard)

    await call.answer()


@dp.callback_query_handler(text='другое')
async def send_msg_other(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
            types.InlineKeyboardButton(
                text=f'{month+1} кв м  ({cell} р)',
                callback_data=f'{month+1, cell}w') for month, cell in enumerate(range(599, 1949+1, 150))
        ]
    keyboard.add(*buttons)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer("Выберите размер ячейки.\nЦена указана за один месяц:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text_contains='w')
async def send_date(call: types.CallbackQuery):
    user_data['size_cell_price'] = re.sub(r'[()w]', '', call.data).split(',')
    buttons = [
        types.InlineKeyboardButton(
            text=f"{month} мес ({month * int(user_data['size_cell_price'][1])} р)", callback_data=f"{month, month * int(user_data['size_cell_price'][1])}h") for month in range(1, 13)
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer("Выберите срок аренды:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text_contains='h')
async def choice_month(call: types.CallbackQuery):
    user_data['rent'] = re.sub(r'[()h]', '', call.data).split(',')
    user_data['total_price'] = user_data['rent'][1]
    keyboard_reg = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    key = types.KeyboardButton(text="Регистрация")
    keyboard_reg.add(key)
    period_days = int(user_data['rent'][0]) * 30.5
    user_data['period_days'] = period_days
    user_data['total_price'] = user_data['total_price']
    user_data['quantity'] = user_data['size_cell_price'][0]
    user_data['item'] = 'другое'

    buttons = [
        types.InlineKeyboardButton(
            text="Забронировать", callback_data='Забронировать')
    ]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*buttons)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer(
        fmt.text(
            fmt.text(fmt.hunderline("Вы выбрали:")),
            fmt.text(f"\nРазмер ячейки:   {user_data['size_cell_price'][0]} кв м"),
            fmt.text(f"\nСрок аренды:   {user_data['rent'][0]} месяцев"),
            fmt.text(f"\nПо адресу:   {user_data['adress']}"),
            fmt.text(f"\nСтоимость итого:   {user_data['total_price']} рублей"), sep="\n",
        ), reply_markup=keyboard,
    )
    await call.answer()


@ dp.callback_query_handler(text='Забронировать')
async def registration(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    user = call.message["chat"]["first_name"]    
    user_id = str(call.from_user.id)
    try:
        with open('clients.json') as f:
            data = json.load(f)
        if user_id in data:
            
            keyboard_ok = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            key_8 = types.KeyboardButton(text='Оплатить')
            key_9 = types.KeyboardButton(text='Отмена')
            keyboard_ok.add(key_8).add(key_9)
            await call.message.answer(f' {user}, вы уже у нас зарегистрированы, рады видеть вас снова! '
                     ' Для оплаты нажмите кнопку ниже:', reply_markup=keyboard_ok)
            await call.answer()
        else:
            keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
            buttons = [
                "Регистрация",
                "Отмена",
            ]
            keyboard.add(*buttons)
            await call.message.answer(f' {user}, вы у нас впервые? Давайте зарегистрируемся.', reply_markup=keyboard)
    except:
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        buttons = [
            "Регистрация",
             "Отмена",
        ]
        keyboard.add(*buttons)
        await call.message.answer(f' {user}, вы у нас впервые? Давайте зарегистрируемся.', reply_markup=keyboard)
            

@dp.message_handler(lambda message: message.text == "Отмена")
async def cancel(message: types.Message):
    await message.answer('Мне жаль, что вы уходите, но если передумаете - нажмите /start')


@dp.message_handler(text="Регистрация")
async def logging(message: types.Message):
    user_id = message.from_user.id
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    buttons = [
        "Принять",
        "Отказаться",
    ]
    keyboard.add(*buttons)
    doc = open('pd.pdf', 'rb')
    await bot.send_document(user_id, doc)
    await bot.send_message(
        user_id,
        "Для заказа нужно Ваше согласие на обработку персональных данных. Пожалуйста, ознакомьтесь.",
        reply_markup=keyboard,
    )


@dp.message_handler(text='Оплатить')
async def pay(message: types.Message):



    PRICE = types.LabeledPrice(label='Склад', amount=30000)
    # PRICE = types.LabeledPrice(label='Склад', amount=user_data['total_price'])
    await bot.send_message(message.from_user.id, message.text)

    if PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.from_user.id, 'Склад в Москве-1')
        print(user_data)
        await bot.send_invoice(
            message.from_user.id,
            title='Склад в Москве',
            description='Склад в Москве очень, очень нужная штука',
            provider_token=PAYMENTS_PROVIDER_TOKEN,
            currency='rub',
            photo_url='https://d.radikal.ru/d42/2111/76/bc089db2ed4d.jpg',
            photo_height=512,
            photo_width=512,
            photo_size=512,
            is_flexible=False,
            prices=[PRICE],
            start_parameter='storage',
            payload='some-invoice'
        )


@dp.pre_checkout_query_handler()
async def precheck(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_buynd(message: types.Message):
    if message.successful_payment.invoice_payload == 'some-invoice':
        keyboard_qr = types.InlineKeyboardMarkup(resize_keyboard=True)
        key = types.InlineKeyboardButton(text='Получить QR чек', callback_data='QR')
        keyboard_qr.add(key)
        await bot.send_message(message.from_user.id, 'Оплачено!', reply_markup=keyboard_qr)


@dp.callback_query_handler(text='QR')
async def send_qrcode(call: types.CallbackQuery):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = f'{call.message.chat.id}_{timestr}.png'
    images_dir = os.path.join(os.getcwd(), 'QR')
    os.makedirs(images_dir, exist_ok=True)
    filepath = os.path.join(images_dir, filename)
    code = f'{timestr}_{call.message.chat.id}_'
    url = pyqrcode.create(code)
    url.png(filepath, scale=15)
    today = date.today()
    storage_date_end = today + timedelta(days=user_data['period_days'])
    storage_date_end = storage_date_end.strftime("%d.%m.%Y")
    storage_date_start = today.strftime("%d.%m.%Y")
    quantity = user_data['quantity']
    quantity = re.findall(r'\d+', quantity)[0]
    user_data['period_days'] = f'{storage_date_start}-{storage_date_end}'

    user_id = str(call.message.chat.id)
    try:
        with open('orders.json') as f:
            data = json.load(f)
        if user_id in data:
            data[user_id].append(user_data)
            with open('orders.json', 'w') as f:
                json.dump(data, f, ensure_ascii=False, default=str)
        else:
            order = {}
            order[call.message.chat.id] = user_data
            with open('orders.json', 'w') as file:
                json.dump(order, file, ensure_ascii=False, default=str)
    except:
        order = {}
        order[call.message.chat.id] = user_data
        with open('orders.json', 'w') as file:
            json.dump(order, file, ensure_ascii=False, default=str)

    await call.message.answer('Заказ создан и успешно оплачен!'
                              ' Вот ваш электронный ключ для доступа к вашему личному складу. '
                              f'Вы сможете попасть на склад в любое время в период с {storage_date_start} по {storage_date_end}')
    photo = open(filepath, 'rb')
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo)
    # keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    # keyboard.add(KeyboardButton(text="В начало"))
    # await bot.delete_message(call.from_user.id, call.message.message_id)
    # await call.answer('Спасибо за заказ! Если хотите сделать еще один - нажмите "В начало" 😉 ', show_alert=True)
    # await bot.send_message(call.from_user.id, 'Еще заказ?', reply_markup=keyboard)
    buttons = [
        types.InlineKeyboardButton(text='Новый заказ', callback_data='start'),
        types.InlineKeyboardButton(text='Посмотреть заказы', callback_data='story'),
               ]

    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer("Спасибо! Что желаете?", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text='story')
async def send_date(call: types.CallbackQuery):
    user_id = str(call.message.chat.id)
    with open('orders.json') as f:
        data = json.load(f)
    print("Ваши заказы:")




@dp.message_handler(state=None)
async def begin(message: types.Message):
    if message.text == 'Принять':
        await FsmAdmin.first_name.set()
        await bot.send_message(message.from_user.id, 'Укажите имя')
    elif message.text == 'Отказаться':
        user_id = message.from_user.id
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(KeyboardButton(text="В начало"))
        await bot.send_message(
            user_id,
            "Извините, без согласия на обработку данных заказы невозможны.", reply_markup=keyboard
        )


@dp.message_handler(state=FsmAdmin.first_name)
async def first_name(message: types.Message, state: FSMContext):
    name = re.findall(r"\b[А-Яа-я]{1,15}\b", message.text, flags=re.I)
    if not name:
        await bot.send_message(message.from_user.id,
                               'Используйте кирилицу, либо превышено количество символов (не более 15)')
    else:
        async with state.proxy() as data:
            data["first_name"] = message.text
        await FsmAdmin.next()
        await bot.send_message(message.from_user.id, 'Укажите фамилию')


@dp.message_handler(state=FsmAdmin.last_name)
async def last_name(message: types.Message, state: FSMContext):
    name = re.findall(r"\b[А-Яа-я]{1,15}\b", message.text, flags=re.I)
    if not name:
        await bot.send_message(message.from_user.id,
                               'Используйте кирилицу, либо превышено количество символов (не более 15)')
    else:
        async with state.proxy() as data:
            data["last_name"] = message.text

        keyboard_ok = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        key_1 = types.KeyboardButton(text='контакт', request_contact=True)
        keyboard_ok.add(key_1)
        await FsmAdmin.next()
        await bot.send_message(message.from_user.id, 'Укажите номер телефона')


@dp.message_handler(state=FsmAdmin.phone)
async def phone(message: types.Message, state: FSMContext):
    phone = re.findall(r"\b[\d+]{10}\b", message.text, flags=re.I)
    if not phone:
        await message.answer('Используйте только цифры, либо превышено количество символов (10 цифр)')
    else:
        async with state.proxy() as data:
            data["phone"] = message.text
        await FsmAdmin.next()
        await message.answer('Укажите номер паспорта в формате: ХХХХ ХХХХХХ')


@dp.message_handler(state=FsmAdmin.passport)
async def passport(message: types.Message, state: FSMContext):
    passp = re.findall(r"[\d+]{4}\s[\d+]{6}", message.text, flags=re.I)
    if not passp:
        await message.answer('Укажите номер паспорта в формате: ХХХХ ХХХХХХ')
    else:
        async with state.proxy() as data:
            data["pasport"] = message.text
        await FsmAdmin.next()
        await message.answer('Укажите дату рождения в формате: ХХ.ХХ.ХХХХ')


@dp.message_handler(state=FsmAdmin.born)
async def born(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, message.text)
    born = re.findall(r"[\d+]{2}.[\d+]{2}.[\d+]{4}", message.text, flags=re.I)
    if not born:
        await message.answer('Используйте только цифры в формате: ХХ.ХХ.ХХХХ')
    else:
        try:
            year = datetime.datetime.today() - datetime.datetime.strptime(message.text, '%d.%m.%Y')
        except:
            await message.answer('Введите корректную дату в формате: ХХ.ХХ.ХХХХ')
        year_old = year.days // 365
        if 14 < year_old < 100:
            async with state.proxy() as data:
                data["born"] = message.text
                user_data['logging'] = str(data)
            keyboard_ok = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            key_8 = types.KeyboardButton(text='Оплатить')
            keyboard_ok.add(key_8)
            await bot.send_message(message.from_user.id, 'Готово!', reply_markup=keyboard_ok)
            await state.finish()
        else:
            await message.answer('Не допустимый возраст. Вам должно быть не менее 14 и не более 100 лет')
            await message.answer('Введите корректную дату в формате: ХХ.ХХ.ХХХХ')

if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=True)
