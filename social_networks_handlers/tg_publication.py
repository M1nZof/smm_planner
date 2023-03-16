import telegram
from environs import Env


def send_telegram_post(post_text, image_name):
    env = Env()
    env.read_env()

    telegram_bot_token = env('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = env('TELEGRAM_CHAT_ID')

    bot = telegram.Bot(token=telegram_bot_token)

    if image_name is None:
        bot.send_message(telegram_chat_id, post_text)
    else:
        with open(image_name, 'rb') as image:
            if len(post_text) < 1000:  # Больше ~1000 символов не отправляется с фоткой
                bot.send_photo(telegram_chat_id, image, post_text)
            else:
                bot.send_photo(telegram_chat_id, image)
                bot.send_message(telegram_chat_id, post_text)
