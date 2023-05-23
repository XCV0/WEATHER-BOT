from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from pyowm.commons.exceptions import NotFoundError
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config
import asyncio

API_TOKEN_aiogram = '6080559644:AAH6i1HGi-tBsLVveSDKEZ_MjuSQOXWkD1Y'
API_TOKEN_owm = "77468d57077a35111fa143607b9b5341"

# Stting PyOWM
config_dict = get_default_config()
config_dict['language'] = 'ru'
owm = OWM(API_TOKEN_owm, config_dict)
mgr = owm.weather_manager()

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN_aiogram)
dp = Dispatcher(bot)

def get_weather_data(city_name):
    observation = mgr.weather_at_place(city_name)
    weather = observation.weather

    output_msg = f"""
Сейчас в городе {city_name[0].upper() + city_name[1:]} {weather.detailed_status}
Температура {str(round(weather.temperature('celsius')['temp']))}°С
"""

    inline_btn_1 = InlineKeyboardButton('Узнать подробнее', callback_data=city_name)
    temp_msg_kb = InlineKeyboardMarkup().add(inline_btn_1)

    return output_msg, temp_msg_kb


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await bot.send_message(message.from_user.id, "Привет!\nЭтот бот поможет вам узнать погоду в любом городе!\nНапишите люой город в котром Вы хоите узнать погоду")


@dp.message_handler(content_types=['text'])
async def check_weather(message: types.Message):
    city_name = (message.text).lower()

    print(str(message.from_user.id) + "" + city_name)

    try:
        output_msg, temp_msg_kb = get_weather_data(city_name)

        await bot.send_message(message.from_user.id, str(output_msg), reply_markup=temp_msg_kb)  

    except NotFoundError:
        try:
            new_text = ''

            for i in str(message.text):
                if i == 'е':
                    new_text = new_text + "ё"
                else:
                    new_text = new_text + str(i)
            
            output_msg, temp_msg_kb = get_weather_data(new_text)

            await bot.send_message(message.from_user.id, output_msg, reply_markup=temp_msg_kb)

        except NotFoundError:
            await bot.send_message(message.from_user.id, "пользователь долбаеб!")


@dp.callback_query_handler(lambda c: c.data != '')
async def process_callback_button1(callback_query: types.CallbackQuery):
    city_name = (callback_query.data).lower()

    observation = mgr.weather_at_place(city_name)
    weather = observation.weather

    output_msg = f"""Сейчас в городе {city_name[0].upper() + city_name[1:]} {weather.detailed_status}
Температура {str(round(weather.temperature('celsius')['temp']))}°С
Влажность составляет {weather.humidity}%
Скорость ветра {str(round(weather.wind()['speed']))} км/ч
    """
    
    await bot.answer_callback_query(callback_query.id, output_msg, show_alert=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)