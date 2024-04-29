from telebot import *
from translatepy import Translator
import requests

app_id = ''  # 08a1342f697f48b0e546fc6c7a8a9dd4
url = ''
bot = telebot.TeleBot('7180907222:AAH1zUaU5LyueaSe0onTiQuOWk04YQLpVfk')

name = ''
city = ''
weather = ''

#Теперь объявим метод для получения текстовых сообщений
@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, "Привет. Как ваше имя?")
        bot.register_next_step_handler(message, get_name) #следующий шаг – функция get_name

#Парсинг json по ключу
def pars(data, key):
    if type(data) is dict:
        if key in data.keys():
            res = data.get(key)
            return res
        else:
            for val in data.values():
                res = pars(val, key)
                if res is not None:
                    return res
    elif type(data) is list:
        for ind in data:
            res = pars(ind, key)
            if res is not None:
                return res

#Запрос имя
def get_name(message):
    global name
    name = message.text
    button1(message)


def get_new_city(message):
    global city
    city = message.text
    button1(message)

def button1(message):
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Погода', callback_data='погода')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Информация о городе', callback_data='инф')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, text='Что вас интересует?', reply_markup=keyboard)

def button2(message):
    keyboard = types.InlineKeyboardMarkup()

    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)

    key_yes = types.InlineKeyboardButton(text='Нет', callback_data='no')  # кнопка «Нет»
    keyboard.add(key_yes)

    # bot.send_message(message.from_user.id, text='Хоти те узнать погоду в каком-нибудь ещё городе?',
    #                  reply_markup=keyboard)
    bot.send_message(message.from_user.id, text='Хотите узнать что-нибудь ещё?',
                     reply_markup=keyboard)

#
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "погода":
        bot.send_message(call.message.chat.id, 'Какой город интересует?')
        bot.register_next_step_handler(call.message, get_city)
    elif call.data == 'инф':
        bot.send_message(call.message.chat.id, 'Какой город интересует?')
        bot.register_next_step_handler(call.message, info_city)
    elif call.data == 'yes':
        # bot.send_message(call.message.chat.id, 'Какой город вас интересует?')
        # bot.register_next_step_handler(call.message, get_new_city)
        bot.send_message(call.message.chat.id, 'Для продолжения введите /continue')
        #print(call.message)
        bot.register_next_step_handler(call.message, button1)
    else:
        bot.send_message(call.message.chat.id, 'Досвидания')

#Информация о городе
def info_city(message):
    s = 'https://ru.wikipedia.org/wiki/{city}'.format(city=message.text)
    bot.send_message(message.from_user.id, s)

    button2(message)

#Запрос города
def get_city(message):
    global city
    dict_out = dict()
    city = message.text
    dict_out = check_city(city)

    for k, v in dict_out.items():
        s = k + ': ' + str(v)
        bot.send_message(message.from_user.id, s)

    button2(message)

# проверка на существвание такого города
def check_city(city):
    dict_out = dict()
    global app_id  # 08a1342f697f48b0e546fc6c7a8a9dd4
    app_id = '08a1342f697f48b0e546fc6c7a8a9dd4'
    global url
    url = 'https://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={app_id}'.format(city=city,
                                                                                                   app_id=app_id)

    city_en = translete(city)
    current_weather(city_en, app_id)
    dct_city = current_weather(city, app_id)
    dict_out = check_request(dct_city)

    # Закрытие соединения с АПИ
    dct_city.close()
    return dict_out

def translete(city):
    translator = Translator()
    return translator.translate(city, 'en')

# функция для запроса текущей температуры
def current_weather(city, app_id):
    # 'https://api.openweathermap.org/api
    return requests.get(url)

# проверка успешности запроса и запись данных в переменную
def check_request(dct_city):
    dict_out = dict()
    if dct_city.ok :
        weath_city = eval(dct_city.text)

        # Передача значений: город, температура, погода
        dict_out['Город'] = pars(weath_city, 'name')
        dict_out['Температура'] = round(float(pars(weath_city, 'temp')) - 273.15, 2) #Пересчет из Кельвина в Цельсия
        dict_out['Погода'] = pars(weath_city, 'description')

    else:
        translator = Translator()
        weath_city = eval(dct_city.text)
        dict_out['Возникла ошибка'] = translator.translate(weath_city.get('message'), 'ru')

    return dict_out

# псотоянный запрос к телеграмм
bot.polling(none_stop=True, interval=0)