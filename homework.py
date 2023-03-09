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

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
dt = DT.datetime.strptime('2023-01-01 04:00:00', '%Y-%m-%d %H:%M:%S')

# Глобальная конфигурация для всех логгеров
logging.basicConfig(
    level=logging.DEBUG,
    filename='homework.log', 
    format='%(asctime)s, %(funcName)s, %(levelname)s, %(message)s'
)


def check_tokens():
    """Проверка доступности переменных окружения."""
    logging.debug('Проверка доступности переменных окружения.')
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logging.critical(
            'Переменное окружение отсутствует! Работа прекращена!!!'
            )
        raise TokensErrorException()
    else:
        logging.debug('Переменное окружение: Ok.')


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logging.debug('Отправлено сообщение в тг.')
        #bot.send_message(TELEGRAM_CHAT_ID, message)
    except ErrorSendMassageException:
        logging.error('Ошибка отправки сообщения в тг.')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-ЯП."""
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )
        logging.debug(homework_statuses)
        return homework_statuses.json()
    except Exception as error:
        print('Error url')


def check_response(response):
    """проверяет ответ API на соответствие документации"""


def parse_status(homework):
    """Извлекает из информации о домашней работе статус."""
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    verdict = HOMEWORK_VERDICTS.get(status)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота:
    1. Сделать запрос к API.
    2. Проверить ответ.
    3. Если есть обновления — получить статус работы из обновления и отправить
    сообщение в Telegram.
    4. Подождать некоторое время и вернуться в пункт 1."""
    check_tokens()
    logging.debug('Запуск бота.')
    bot = Bot(TELEGRAM_TOKEN)
    #timestamp = int(time.time())
    timestamp = int(dt.timestamp())
    status = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = response['homeworks'][0]
            check_response(homework)
            new_status = parse_status(homework)
            if new_status != status:
                logging.debug(new_status)
                send_message(bot, message=new_status)
                status = new_status
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
