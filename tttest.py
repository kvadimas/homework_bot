import datetime as DT
import logging
import os
import time
from pprint import pprint
from logging.handlers import RotatingFileHandler

import requests
from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

from exceptions import *

load_dotenv()
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def check_tokens():
    """проверяет доступность переменных окружения"""
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        print(1)
    else:
        print(2)
check_tokens()

a = 2
if isinstance(a, int):
    print(3)
try:
    isinstance(a, dict)
    print(4)
except ErrorAPIException as x:
    print(x)