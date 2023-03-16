import telegram

from google_handlers.google_document_functions import collecting_google_document


def send_telegram_post(telegram_bot_token, telegram_chat_id, post):
    bot = telegram.Bot(token=telegram_bot_token)
    link_google_document = post['link_google_document']
    text = collecting_google_document(link_google_document)

    if post.get('photo_url') is None:
        bot.send_message(telegram_chat_id, text)
    else:
        if len(text) < 1000:  # Больше ~1000 символов не отправляется с фоткой
            bot.send_photo(telegram_chat_id, post['photo_url'], text)
        else:
            bot.send_photo(telegram_chat_id, post['photo_url'])
            bot.send_message(telegram_chat_id, text)
