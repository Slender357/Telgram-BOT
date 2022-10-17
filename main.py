import telebot
from telebot import types as tp
import requests
import re
import phonenumbers

bot = telebot.TeleBot('***')

user_dict = {}
url = '***'
headers = {'Accept': 'application/json'}


class User:
    def __init__(self, number):
        self.number = number
        self.text = None


@bot.message_handler(commands=['start'])
def start(message):
    start = tp.InlineKeyboardButton('Отправить обращение')
    mess = f'Привет @{message.from_user.username}\nЭто решатель проблем в ***. \n\nЧтобы сообщить свою проблему, которая относится к работе нажмите кнопку "Отправить обращение"\n\n*** ответит вам в течение суток.'
    markup = tp.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(start)
    bot.send_message(message.chat.id, mess, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Отправить обращение')
def send_order(message):
    markup = tp.ReplyKeyboardRemove()
    msg = bot.reply_to(message, 'Введите номер телефона', reply_markup=markup)
    bot.register_next_step_handler(msg, process_number_step)


def process_number_step(message):
    try:
        chat_id = message.chat.id
        number = re.sub('[-+/\'.& )( ]', '', message.text)
        if number[0] == '8' or number[0] == '7':
            number = '+7' + number[1:]
        elif number[0] == '9':
            number = '+7' + number
        if len(number) == 12 and int(number[2]) == 9:
            phonenumbers.parse(number)
            user = User(number)
            user_dict[chat_id] = user
            msg = bot.reply_to(message, 'Напишите вашу проблему')
            bot.register_next_step_handler(msg, process_text_step)
        else:
            msg = bot.reply_to(message, 'Введите корректный номер')
            bot.register_next_step_handler(msg, process_number_step)
    except BaseException:
        msg = bot.reply_to(message, 'Введите корректный номер')
        bot.register_next_step_handler(msg, process_number_step)


def process_text_step(message):
    try:
        chat_id = message.chat.id
        textt = message.text
        user = user_dict[chat_id]
        user.text = textt
        order = tp.InlineKeyboardButton('Отправить обращение')
        mess = 'Спасибо ваше сообщение отправлено\n\nЧтобы отправить новое обращение нажмите кнопку "Отправить обращение"'
        markup = tp.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(order)
        data = {
            "title": user.text,
            "description": f'@{message.from_user.username}\n{user.number}\n{user.text}',
            "members": [],
            "links": []
        }
        requests.post(url=url, json=data, headers=headers)
        bot.send_message(message.chat.id, mess, reply_markup=markup)
        user_dict.pop(chat_id)
    except BaseException:
        msg = bot.reply_to(message, 'Введите корректные данные')
        bot.register_next_step_handler(msg, process_text_step)



bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()

bot.infinity_polling()
