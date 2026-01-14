import os
import sys

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..','backend')
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'bricky.settings'
)

import django
django.setup()
import telebot
from environs import Env
from users.models import *
from store.models import *
from orders.models import *
from telebot import types

env = Env()
env.read_env()
bot = telebot.TeleBot(env.str("TG_TOKEN"))
pay_token = env.str("PAY_TOKEN")
user_state = {}
user_data = {}

def create_user(message):
    try:
        user = CustomUser.objects.get(tg_id=message.chat.id)
        bot.send_message(message.chat.id, f"You registered as {user.username}")
    except:
        user = CustomUser.objects.get(email=message.text.strip())
        user.update(tg_id=message.chat_id)
        bot.send_message(message.chat.id, f"You registered as {user.username}")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,"Hello")
    bot.register_next_step_handler(message,create_user)

bot.infinity_polling()