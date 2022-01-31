#!/usr/bin/env python3
from aiogram import Bot, Dispatcher, types,executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pickle

import string
# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
import json

BOT_TOKEN = "5050407246:AAGAVbFGDw6zc60M43FFODhVhjK93i6T_PU"

ADMIN_CHAT_ID_LIST=[]
FIREFIGHTER_CHAT_ID_LIST=[]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)



button1 = InlineKeyboardButton(text="👨‍🔥 FIREFIGHTER", callback_data="fire")
button2 = InlineKeyboardButton(text="👨💰 ADMIN", callback_data="business")
keyboard_inline = InlineKeyboardMarkup().add(button1, button2)

button3 = InlineKeyboardButton(text="🛸 DRONES ", callback_data="drones")
button4 = InlineKeyboardButton(text="💧 LAKES", callback_data="lakes")
keyboard_FIRE = InlineKeyboardMarkup().add(button3, button4)

Settings = json.load(open("Settings.json"))
# ThingsBoard REST API URL
url = Settings['URL']
# Default Tenant Administrator credentials
username = Settings['USERNAME']
password = Settings['PASSWORD']
dronesIDList = []
lakesIDList = []

subStationIDList=[]






with RestClientCE(base_url=url) as rest_client:
    rest_client.login(username=username, password=password)
    assets = rest_client.get_tenant_assets(page_size=1, page=1, type="SubStation")
    lakes = rest_client.get_tenant_devices(page_size=1, page=1, type="Firention_Lakes_Heroku")
    assetsNum = assets.total_pages
    lakesNum = lakes.total_pages
    for i in range(1, assetsNum + 1):
        tmp1 = InlineKeyboardButton(text=f'📡 Substation 00{i}', callback_data=f'SubStation00{i}')
        tmp2 = InlineKeyboardButton(text=f'🛸 Drone {i}', callback_data=f'Firention_Drone_{i}')

        if i == 1:
            keyboard_ADMIN = InlineKeyboardMarkup(resize_keyboard=True).add(tmp1)
            keyboard_DRONES = InlineKeyboardMarkup(resize_keyboard=True).add(tmp2)
        else:
            keyboard_ADMIN.add(tmp1)
            keyboard_DRONES.add(tmp2)

        findDevice = rest_client.get_tenant_device(f'Firention_Drone_{i}')
        deviceToSave = findDevice.id
        dronesIDList.append(deviceToSave)

        findAsset = rest_client.get_tenant_asset(f'SubStation00{i}')
        assetToSave = findAsset.id
        subStationIDList.append(assetToSave)




    for i in range(0, lakesNum):
        tmp3 = InlineKeyboardButton(text=f'💧 Lake {i}', callback_data=f'Firention_Lake_{i}')
        if i == 0:
            keyboard_LAKES = InlineKeyboardMarkup(resize_keyboard=True).add(tmp3)
        else:
            keyboard_LAKES.add(tmp3)
        findDevice = rest_client.get_tenant_device(f'Firention_Lake_{i}')
        deviceToSave = findDevice.id
        lakesIDList.append(deviceToSave)

    droneNameList = [f'Firention_Drone_{i}' for i in range(1, assetsNum + 1)]
    SubNameList = [f'SubStation00{i}' for i in range(1, assetsNum + 1)]
    lakeNameList = [f'Firention_Lake_{i}' for i in range(0, lakesNum)]


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.answer(
        f"Hello, {message.from_user.get_mention(as_html=True)}👋!\nThis is your personal Firention Bot. To start it is better to identify yourself, with the command /identity, to address the best contents for you",
        parse_mode=types.ParseMode.HTML,
    )

@dp.message_handler(commands=['identity'])
async def commandDashboard(message: types.Message):

    await message.answer(
        f"Select the dashboard that you want to see !",
        reply_markup=keyboard_inline
    )


@dp.callback_query_handler(text=["fire", "business"])
async def roleAnswer(call: types.CallbackQuery):

    ID=call.from_user.id

    if call.data == "fire":
        if (ID in ADMIN_CHAT_ID_LIST):
            ADMIN_CHAT_ID_LIST.remove(ID)
        if (ID not in FIREFIGHTER_CHAT_ID_LIST):
            FIREFIGHTER_CHAT_ID_LIST.append(ID)

        shared= [FIREFIGHTER_CHAT_ID_LIST,ADMIN_CHAT_ID_LIST]
        fp = open("shared.pkl", "wb")
        pickle.dump(shared, fp)
        await call.message.answer(
            f"Select the data to retrieve !",
            reply_markup=keyboard_FIRE
        )
    if call.data == "business":
        if (ID in FIREFIGHTER_CHAT_ID_LIST):
            FIREFIGHTER_CHAT_ID_LIST.remove(ID)
        if (ID not in ADMIN_CHAT_ID_LIST):
            ADMIN_CHAT_ID_LIST.append(ID)
        shared = [FIREFIGHTER_CHAT_ID_LIST,ADMIN_CHAT_ID_LIST]
        fp = open("shared.pkl", "wb")
        pickle.dump(shared, fp)
        await call.message.answer(
            f"Select the substation that you want to analyze !",
            reply_markup=keyboard_ADMIN
        )
    await call.answer()


@dp.callback_query_handler(text=["lakes", "drones"])
async def fireFighterAnswer(call: types.CallbackQuery):
    if call.data == "lakes":
        await call.message.answer(
            f"Select the lake to retrieve info on it!",
            reply_markup=keyboard_LAKES
        )
    if call.data == "drones":
        await call.message.answer(
            f"Select the drone to retrieve info on it!",
            reply_markup=keyboard_DRONES
        )
    await call.answer()


@dp.callback_query_handler(text=lakeNameList)
async def lakesAnswer(call: types.CallbackQuery):
    name=call.data
    name_splitted=name.split('_')
    index=int(name_splitted[2])
    res = rest_client.get_latest_timeseries(entity_type=lakesIDList[index].entity_type, entity_id=lakesIDList[index].id)
    lake_name=res['name'][0]['value']
    latitude = res['latitude'][0]['value']
    longitude = res['longitude'][0]['value']
    value = res['value'][0]['value']
    value_max = res['value_max'][0]['value']
    percentage = res['percentage'][0]['value']
    link=f'https://www.google.com/maps/search/?api=1&query={latitude}%2C{str(longitude)}'
    for elem in string.whitespace:
        link = link.replace(elem, '')
    msgToSend=f'{name} :\n-> Lake name: {lake_name}\n-> Actual value: {value}\n-> Value Max: {value_max}\n-> Percentage: {percentage}\n{link}'
    await call.message.answer(msgToSend)
    await call.answer()



@dp.callback_query_handler(text=SubNameList)
async def subAnswer(call: types.CallbackQuery):
    name=call.data
    index=int(name[-1])
    res = rest_client.get_latest_timeseries(entity_type=subStationIDList[index-1].entity_type, entity_id=subStationIDList[index-1].id)
    res2=rest_client.get_attributes(entity_type=subStationIDList[index-1].entity_type, entity_id=subStationIDList[index-1].id)
    temperature=res['temperature'][0]['value']
    online_temperature = res['online_temperature'][0]['value']
    humidity = res['humidity'][0]['value']
    online_humidity = res['online_humidity'][0]['value']
    smoke = res['smoke'][0]['value']
    movement = res['isMovementDetected'][0]['value']
    wind_direction = res['wind_direction'][0]['value']
    anem_data = res['anem_data'][0]['value']
    latitude= res2[0]['value']
    longitude= res2[1]['value']
    link=f'https://www.google.com/maps/search/?api=1&query={latitude}%2C{str(longitude)}'
    for elem in string.whitespace:
        link = link.replace(elem, '')
    msgToSend=f'{name} :\n->Temperature:\n ===>Station: {temperature}ºC\n===>Online: {online_temperature}ºC\n -> Humidity:\n===>Station: {humidity}%\n===>Online: {online_humidity}%\n-> Smoke: {smoke} % of CO2\n-> Movement detected: {movement}\n->Wind Direction: {wind_direction} º\n->Wind Speed: {anem_data}m/s\n{link}'
    await call.message.answer(msgToSend)
    await call.answer()


@dp.callback_query_handler(text=droneNameList)
async def dronesAnswer(call: types.CallbackQuery):

    name=call.data
    name_splitted = name.split('_')
    index = int(name_splitted[2])
    res = rest_client.get_latest_timeseries(entity_type=dronesIDList[index - 1].entity_type,
                                            entity_id=dronesIDList[index - 1].id)
    flightMode = res['drone_flightMode'][0]['value']
    drone_latitude = res['drone_latitude'][0]['value']
    drone_longitude = res['drone_longitude'][0]['value']
    drone_altitude = res['drone_altitude'][0]['value']
    drone_battery = res['drone_battery'][0]['value']
    drone_isFireDetected = res['drone_isFireDetected'][0]['value']
    link = f'https://www.google.com/maps/search/?api=1&query={drone_latitude}%2C{str(drone_longitude)}'
    for elem in string.whitespace:
        link = link.replace(elem, '')
    msgToSend = f'{name} :\n-> Flight mode: {flightMode}\n-> Altitude: {drone_altitude}\n-> Battery: {drone_battery}\n-> Fire Detected: {drone_isFireDetected}\n{link}'
    await call.message.answer(msgToSend)
    await call.answer()


if __name__ == '__main__':



    executor.start_polling(dp)
