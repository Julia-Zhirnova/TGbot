import telebot
bot = telebot.TeleBot('6829414239:AAFwufvQ6jPB9GYaiRRLfRY50XFc7atfZ1I')
from telebot import types
import re
import requests
import json
import datetime
import pytz
import traceback

P_TIMEZONE = pytz.timezone('Europe/Moscow')
TIMEZONE_COMMON_NAME = 'Moscow'

URL = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'

def load_exchange():
    return json.loads(requests.get(URL).text)


def get_exchange(ccy_key):
    for exc in load_exchange():
        if ccy_key == exc['ccy']:
            return exc
    return False


def get_exchanges(ccy_pattern):
    result = []
    ccy_pattern = re.escape(ccy_pattern) + '.*'
    for exc in load_exchange():
        if re.match(ccy_pattern, exc['ccy'], re.IGNORECASE) is not None:
            result.append(exc)
    return result

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши Привет, /python или /exchange, чтобы узнать курс валют")
    elif message.text == "/exchange":
        mesg = bot.send_message(message.chat.id, 'Начнем?')
        bot.register_next_step_handler(mesg, exchange_command)
    elif message.text == "/python":
        mesg = bot.send_message(message.chat.id, 'Начнем?')
        bot.register_next_step_handler(mesg, get_python)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")
def get_python(message):
    keyboard = types.InlineKeyboardMarkup() #наша клавиатура
    key_history = types.InlineKeyboardButton(text='Сферы применения языка Python', callback_data='history')
    keyboard.add(key_history) #добавляем кнопку в клавиатуру
    key_features= types.InlineKeyboardButton(text='Типы данных и операторы', callback_data='features')
    keyboard.add(key_features)
    key_type = types.InlineKeyboardButton(text='Функции', callback_data='type')
    keyboard.add(key_type)
    key_structure = types.InlineKeyboardButton(text='Синхронное и асинхронное выполнение функций', callback_data='structure')
    keyboard.add(key_structure)
    question = 'Что тебя интересует по Python?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

def exchange_command(message):
    keyboard = types.InlineKeyboardMarkup()
    key_money = types.InlineKeyboardButton(text='USD', callback_data='get-USD')
    keyboard.add(key_money)  # добавляем кнопку в клавиатуру
    bot.send_message(
        message.chat.id,
        'Click on the currency of choice:',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "history": #call.data это callback_data, которую мы указали при объявлении кнопки
        #код сохранения данных, или их обработки
        bot.send_message(call.message.chat.id,
        '1.	Web-разработка. Всю серверную часть веб-сайта можно написать на Python. Но не на чистом Python, а на популярных фреймворках (Django, Flask), которые, в свою очередь, написаны на нем.\n'
        '2.	Разработка программ с графическим пользовательским интерфейсом. В данной области также можно использовать Python и его библиотеки (например, PythonCard).\n'
        '3.	Базы данных. Python умеет просто взаимодействовать с любами базами данных.\n'
        '4.	Системное администрирование. У Python есть интерфейсы для управления службами различных операционных систем, в которых он работает.\n'
        '5.	Научные исследования. В Python есть библиотеки, которые пригодятся для проведения исследований и вычислений (NumPy, Matplolib).\n'
        '6.	Машинное обучение. Здесь активно используются Python, и его дополнительные библиотеки, «заточенные» специально под работу с моделями машинного обучения.')
    elif call.data == "features":
        bot.send_message(call.message.chat.id, '1. Целые числа и математические операторы\n'
                                               '2. Булевые и логические операторы.\n')
    elif call.data == "type":
        bot.send_message(call.message.chat.id, 'Функция – именованный блок кода, который изолирован от остальной программы и выполняются только тогда, когда вызываются. \n'
                                               'Для создания функции необходимо ее объявить с помощью ключевого слова def. Далее необходимо указать имя функции и параметры функции (если нужно).\n'
                                               'Параметры функции – это некоторая информация, которая нужна для работы функции. Эта информация заключается в круглые скобки. Определение функции заканчивается двоеточием.\n'
                                               'Далее идут строки кода с отступом – описание того, что делает функция.')
    elif call.data == "structure":
        bot.send_message(call.message.chat.id, 'Асинхронные функции – это специальный тип функций, которые позволяют выполнить несколько задач одновременно без блокировки основного потока выполнения программы.\n'
                                               ' Асинхронные функции могут выполняться параллельно, т.е. одна задача может начинаться, даже если другая еще не закончилась. Это позволяет значительно ускорить выполнение программы,\n'
                                               'особенно если в ней есть задачи, которые могут выполняться параллельно, например, чтение и запись файлов или обработка запросов к сети.')
def iq_callback(query):
    data = query.data
    if data.startswith('get-'):
        get_ex_callback(query)
def get_ex_callback(query):
    bot.answer_callback_query(query.id)
    send_exchange_result(query.message, query.data[4:])
def send_exchange_result(message, ex_code):
    bot.send_chat_action(message.chat.id, 'typing')
    ex = get_exchange(ex_code)
    bot.send_message(
        message.chat.id, serialize_ex(ex),
	parse_mode='HTML'
    )
def serialize_ex(ex_json, diff=None):
    result = '<b>' + ex_json['base_ccy'] + ' -> ' + ex_json['ccy'] + ':</b>\n\n' + \
             'Buy: ' + ex_json['buy'] + '\nSell: ' + ex_json['sale'] + '\n'
    return result

if __name__ == '__main__':
    while True:
        # в бесконечном цикле постоянно опрашиваем бота — есть ли новые сообщения
        try:
            bot.polling(none_stop=True, interval=0)
        # если возникла ошибка — сообщаем про исключение и продолжаем работу
        except Exception as e:
            print('Сработало исключение!')





