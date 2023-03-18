import requests
import telegram

from environs import Env

from errors_classes import SocialNetworkError


def send_telegram_post(post_text, image_name):
    env = Env()
    env.read_env()

    telegram_bot_token, telegram_chat_id = get_telegram_environs()

    bot = telegram.Bot(token=telegram_bot_token)

    try:
        if image_name is None:
            message = bot.send_message(telegram_chat_id, post_text)
            id_ = get_telegram_message_id(message)
            return id_
        else:
            with open(image_name, 'rb') as image:
                if len(post_text) < 1000:  # Больше ~1000 символов не отправляется с фоткой
                    message = bot.send_photo(telegram_chat_id, image, post_text)
                    id_ = get_telegram_message_id(message)
                    return id_
                else:
                    ids = []
                    message_with_photo = bot.send_photo(telegram_chat_id, image)
                    message = bot.send_message(telegram_chat_id, post_text)
                    ids.append(get_telegram_message_id(message_with_photo))
                    ids.append(get_telegram_message_id(message))
                    return ids

    except telegram.error.TelegramError('tg_error'):
        raise SocialNetworkError('Telegram error')

    except requests.exceptions.HTTPError:
        raise requests.exceptions.HTTPError

    except requests.exceptions.ConnectionError:
        raise requests.exceptions.ConnectionError


def delete_telegram_post(message_id):
    telegram_bot_token, telegram_chat_id = get_telegram_environs()
    bot = telegram.Bot(token=telegram_bot_token)

    try:
        message_id = message_id.split(', ')
        for message in message_id:
            bot.delete_message(telegram_chat_id, message)
    except TypeError:
        bot.delete_message(telegram_chat_id, int(message_id))


def get_telegram_message_id(message):
    if isinstance(message, list):
        ids = []
        for post in message:
            ids.append(post['message_id'])
        return ids
    else:
        return message['message_id']


def get_telegram_environs():
    env = Env()
    env.read_env()

    telegram_bot_token = env('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = env('TELEGRAM_CHAT_ID')

    return telegram_bot_token, telegram_chat_id
