from urllib import parse

import gspread
import requests

from google_handlers import sheet_functions

from pathlib import Path
from environs import Env

from social_networks_handlers import vk_publication, ok_publication

GOOGLE_CREDENTIALS = gspread.service_account(Path.joinpath(Path.cwd(), 'service_account.json').__str__())
SPREADSHEET = GOOGLE_CREDENTIALS.open('smm-planer-table')
WORKSHEET = SPREADSHEET.sheet1


def main():
    env = Env()
    env.read_env()

    # telegram_bot_token = env('TELEGRAM_BOT_TOKEN')
    # telegram_chat_id = env('TELEGRAM_CHAT_ID')
    #
    # while True:
    #     all_posts = sheet_functions.get_all_records()
    #
    #     for post_number, post in enumerate(all_posts, start=2):
    #         formatted_datetime = sheet_functions.get_formatted_datetime(post)
    #         datetime_now = sheet_functions.get_datetime_now()
    #
    #         if formatted_datetime <= datetime_now and post['public_fact'] != '':
    #             send_telegram_post(telegram_bot_token, telegram_chat_id, post)
    #             sheet_functions.post_cell_text(post_number, 7, datetime_now)
    #             time.sleep(300)

    # всего постов
    posts_count = sheet_functions.get_posts_count()

    # задаем номер публикуемого поста
    post_number = 5

    # проверяем на верность
    if post_number > posts_count:
        print(f'{post_number} - неверный номер поста')
        exit()

    # получаем текст поста и имя файла картинки
    post_text, image_file_name = get_posts_text_imagefile(post_number)

    # публикуем пост Вконтаке
    vk_publication.publication_post_vk(post_text, image_file_name)

    # публикуем пост в Одноклассниках
    ok_publication.publication_post_ok(post_text, image_file_name)


def get_posts_text_imagefile(post_number):
    all_posts = sheet_functions.get_all_records()
    post = all_posts[post_number - 1]
    image_file_name = Path(parse.urlsplit(post['photo_url']).path).name

    all_posts = sheet_functions.get_all_posts()

    # send_telegram_post(telegram_bot_token, telegram_chat_id, post)
    post_image = requests.get(post['photo_url'])
    post_image.raise_for_status()

    file_path = Path.cwd()
    with open(Path.joinpath(file_path, image_file_name), 'wb') as file:
        file.write(post_image.content)

    post_text = sheet_functions.get_post_text(post)
    return post_text, image_file_name


if __name__ == '__main__':
    main()
