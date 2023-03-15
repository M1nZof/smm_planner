import gdown
import gspread
import telegram
import json

from bs4 import BeautifulSoup
from pathlib import Path
from environs import Env
from urllib.parse import urlparse


def send_post(telegram_bot_token, telegram_chat_id, post):
    bot = telegram.Bot(token=telegram_bot_token)
    output = str(urlparse(post['link_google_document']).path.split('/')[-2])
    gdown.download(url=post['link_google_document'], output=output, fuzzy=True, quiet=True)
    with open(output, 'r', encoding='UTF-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        scripts = soup.find_all({'script': 'nonce'})
        text = ''
        for script in scripts:
            if script.text.startswith('DOCS_modelChunk ='):
                text = script.text.replace('DOCS_modelChunk = ', '')
                excess_text_part_char = text.find('; DOCS_modelChunkLoadStart')
                text = text[:excess_text_part_char]
                text = json.loads(text)[0]['s']
                break

    if post.get('photo_url') is None:
        bot.send_message(telegram_chat_id, text)
    else:
        if len(text) < 1000:  # Больше ~1000 символов не отправляется с фоткой
            bot.send_photo(telegram_chat_id, post['photo_url'], text)
        else:
            bot.send_photo(telegram_chat_id, post['photo_url'])
            bot.send_message(telegram_chat_id, text)


def main():
    env = Env()
    env.read_env()

    vk_access_token = env.str('VK_ACCESS_TOKEN')
    vk_group_id = env.int('VK_GROUP_ID')
    vk_authorization = {'Authorization': f'Bearer {vk_access_token}'}

    telegram_chat_id = env.str('TELEGRAM_CHAT_ID')
    telegram_bot_token = env.str('TELEGRAM_BOT_TOKEN')

    gc = gspread.service_account(Path.joinpath(Path.cwd(), 'service_account.json').__str__())
    sh = gc.open('smm-planer-table')

    titles = sh.sheet1.row_values(1)
    row = sh.sheet1.row_values(5)
    post = {}
    for index, title in enumerate(titles):
        try:
            if row[index] == '':
                row[index] = None
            post[title] = row[index]
        except IndexError:
            post[title] = None
    send_post(telegram_bot_token, telegram_chat_id, post)


if __name__ == '__main__':
    main()
