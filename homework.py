import datetime as DT
import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import JsonError, TokensErrorException

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
# ОТЛАДКА.
time_test = int(DT.datetime.strptime(
    '2023-01-01 04:00:00',
    '%Y-%m-%d %H:%M:%S'
).timestamp())
# timestamp = time_test

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
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception:
        logging.error('Ошибка отправки сообщения')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-ЯП."""
    payload = {'from_date': timestamp}
    logging.debug('Запрос к эндпоинту API-ЯП.')
    try:
        request = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )
        logging.debug(f'Ответ получен. Статус:{request.status_code}')
    except requests.exceptions.HTTPError as error:
        raise error('Сервер API-ЯП недоступен!')
    except requests.exceptions.ConnectionError as error:
        raise error('Неполадки в сети!')
    except requests.exceptions.RequestException as error:
        raise error('Ошибка в ответе от сервера!')
    if request.status_code != HTTPStatus.OK:
        raise ValueError(f'Код ответа от API {request.status_code}')
    try:
        homework = request.json()
    except JsonError as error:
        raise error('Ошибка json.')
    return homework


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    logging.debug('Проверка ответа API:')
    if not isinstance(response, dict):
        raise TypeError('Не корректный ответ от API!')
    else:
        logging.debug('OK')
    if 'homeworks' not in response:
        raise TypeError('В ответе API домашки нет ключа homeworks!')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Не верный тип данных от API!')
    return response


def parse_status(homework):
    """Извлекает из информации о домашней работе статус."""
    if 'homework_name' not in homework:
        raise KeyError('в ответе API нет ключа homework_name')
    homework_name = homework['homework_name']
    status = homework['status']
    if status not in HOMEWORK_VERDICTS:
        raise ValueError('API возвращает недокументированный статус')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """
    Основная логика работы бота.
    1. Сделать запрос к API.
    2. Проверить ответ.
    3. Если есть обновления — получить статус работы из обновления и отправить
    сообщение в Telegram.
    4. Подождать некоторое время и вернуться в пункт 1.
    """
    check_tokens()
    logging.debug('Запуск бота.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    status = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)['homeworks'][0]
            if homework.get('status') != status:
                message = parse_status(homework)
                logging.info(message)
                send_message(bot, message=message)
                status = homework.get('status')
            else:
                logging.debug('Нет новых статусов.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
