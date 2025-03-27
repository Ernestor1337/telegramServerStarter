from telebot import TeleBot, types
from datetime import datetime as dt
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import psutil
import subprocess

load_dotenv()

# Логирование
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('main.log', maxBytes=500000, backupCount=5, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
admins = os.getenv('ADMINS')
bot = TeleBot(token=os.getenv('TOKEN'))
commands = ['/help', '/start', '/time', '/server']

# Создание клавиатуры
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_help = types.KeyboardButton('/help')
button_time = types.KeyboardButton('/time')
button_server = types.KeyboardButton('/server')
button_stopserver = types.KeyboardButton('/stopserver')
keyboard.add(button_time, button_help, button_server, button_stopserver, row_width=3)


# Проверяем если сервер запущен
def is_jar_running(jar_name):
    for proc in psutil.process_iter(['cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any(jar_name in arg for arg in cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


jar_path = r'C:/minecraftServer/server_starter.jar'
jar_name = "server_starter.jar"


def chatDefiner(message):
    return message.chat.id


def nameDefiner(message):
    return message.chat.first_name


@bot.message_handler(commands=['help'])
def timeInPrague(message):
    bot.send_message(chat_id=chatDefiner(message), text=f'Все возможные команды: {commands}')


@bot.message_handler(commands=['time'])
def timeInPrague(message):
    bot.send_message(chat_id=chatDefiner(message), text=f'Time in Prague is {dt.now()}')


@bot.message_handler(commands=['start'])
def say_hi(message):
    bot.send_message(chat_id=chatDefiner(message),
                     text=f'Привет {nameDefiner(message)}, я ErnestoThoughts!',
                     reply_markup=keyboard)


@bot.message_handler(commands=['server'])
def start_server(message):
    if not is_jar_running(jar_name):
        subprocess.Popen(["java", "-jar", jar_path])
        logging.warning('Server is starting!')
        bot.send_message(chat_id=chatDefiner(message),
                         text=f'Сервер запускается! Это займет лишь пару минут')
        bot.send_message(chat_id=chatDefiner(message),
                         text=f'ip: friends-surfing.gl.joinmc.link. Версия сервера: 1.21.5')
    else:
        bot.send_message(chat_id=chatDefiner(message),
                         text="Сервер уже запущен! ip: friends-surfing.gl.joinmc.link")


@bot.message_handler(commands=['stopserver'])
def close_server(message):
    if str(message.from_user.id) in admins:
        bot.reply_to(message, text=('Сервер выключен'))
        try:
            for proc in psutil.process_iter(['pid', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any(jar_name in arg for arg in cmdline):
                        logging.warning('Server is turning off')
                        proc.terminate()  # Graceful termination
                        proc.terminate()
                        proc.wait()  # Wait for the process to close
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except:
            bot.send_message(chat_id=chatDefiner(message), text="Сервер выключен, или возникла какая-то ошибка")
    else:
        bot.reply_to(message, text="❌ Вы не можете использовать эту команду")
        logging.info(f'{chatDefiner(message)} tried to turn server off')


@bot.message_handler(content_types=['voice', 'video'])
def no_reply(message):
    bot.send_message(chat_id=chatDefiner(message),
                     text=f'К сожалению, я умею работать только с текстом и командами')


@bot.message_handler(content_types=['text'])
def regular_text(message):
    bot.send_message(chat_id=chatDefiner(message),
                     text=f'Привет {nameDefiner(message)}, '
                          f'я советую тебе использовать команды, чтобы оценить все возможности!')


if __name__ == '__main__':
    bot.polling(interval=2)
