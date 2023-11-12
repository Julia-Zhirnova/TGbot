import telebot
token="6914623824:AAG2rJrLgGKSg1RxqklhiwQzMP5E8n4ZlVA"
from telebot import types
bot =telebot.TeleBot(token)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Ваше приветствие")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши Привет, название города или /python")
    elif message.text == "/python":
        mesg = bot.send_message(message.chat.id, 'Начнем?')
        bot.register_next_step_handler(mesg, get_python)
    else:
        bot.send_message(message.from_user.id, "Не понимаю, нужен /help")
def get_python(message):
    keyboard = types.InlineKeyboardMarkup() #наша клавиатура
    key_history = types.InlineKeyboardButton(text='Этапы развития языка Python', callback_data='history')
    keyboard.add(key_history) #добавляем кнопку в клавиатуру
    question = 'Что тебя интересует по Python?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "history": #call.data это callback_data, которую мы указали при объявлении кнопки
        #код сохранения данных, или их обработки
        bot.send_message(call.message.chat.id,
        '....')

if __name__ == '__main__':
    while True:
        # в бесконечном цикле постоянно опрашиваем бота — есть ли новые сообщения
        try:
            bot.polling(none_stop=True, interval=0)
        # если возникла ошибка — сообщаем про исключение и продолжаем работу
        except Exception as e:
            print('Сработало исключение!')
