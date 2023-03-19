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
            message_id = get_telegram_message_id(message)
            return message_id
        else:
            with open(image_name, 'rb') as image:
                if len(post_text) < 1000:  # Больше ~1000 символов не отправляется с фоткой
                    message = bot.send_photo(telegram_chat_id, image, post_text)
                    message_id = get_telegram_message_id(message)
                    return message_id
                else:
                    ids = []
                    message_id_with_photo = bot.send_photo(telegram_chat_id, image)
                    message_id = bot.send_message(telegram_chat_id, post_text)
                    ids.append(get_telegram_message_id(message_id_with_photo))
                    ids.append(get_telegram_message_id(message_id))
                    return ids

    except telegram.error.TelegramError:
        raise SocialNetworkError({'col': 5, 'message': 'inner_tg_error'})
        # Передается словарь со столбцом чек-листа соцсети и сообщением об ошибке. Тут заглушка, мне было лень
        # кидать нормальный error

    except requests.exceptions.HTTPError:
        raise requests.exceptions.HTTPError(col=5)

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
