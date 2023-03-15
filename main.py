import gspread
import telegram


from pathlib import Path
from environs import Env


def send_post(telegram_bot_token, telegram_chat_id, post):
    bot = telegram.Bot(token=telegram_bot_token)
    bot.send_message(telegram_chat_id, post)


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
