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

print(int(DT.datetime.strptime(
                    '2023-03-13T12:05:27',
                    '%Y-%m-%dT%H:%M:%S'
                ).timestamp()))