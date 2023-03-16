import time
from urllib import parse

import requests

from google_handlers import sheet_functions

from pathlib import Path
from environs import Env

from social_networks_handlers.ok_publication import publication_post_ok
from social_networks_handlers.tg_publication import send_telegram_post
from social_networks_handlers.vk_publication import publication_post_vk


def main():
    env = Env()
    env.read_env()

    telegram_bot_token = env('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = env('TELEGRAM_CHAT_ID')

    while True:
        all_posts = sheet_functions.get_all_records()

        for post_number, post in enumerate(all_posts, start=2):
            formatted_datetime = sheet_functions.get_formatted_datetime(post)
            datetime_now = sheet_functions.get_datetime_now()

            if formatted_datetime <= datetime_now and post['public_fact'] == '': # TODO убрать проверку факта публикации
                post_text, image_file_name = get_posts_text_imagefile(post_number)
                if post['social_network'] == 'Telegram':
                    send_telegram_post(telegram_bot_token, telegram_chat_id, post)
                elif post['social_network'] == 'VK':
                    publication_post_vk(post_text, image_file_name)
                elif post['social_network'] == 'OK':
                    publication_post_ok(post_text, image_file_name)

                sheet_functions.post_cell_text(post_number, 7, str(datetime_now))
                time.sleep(300)


        Path(Path.cwd(), 'temp_post_file').unlink()  # удаляем этот временный файл с html поста
        Path(Path.joinpath(Path.cwd(), image_file_name)).unlink()  # удаляем файл изображения


def get_posts_text_imagefile(post):
    image_file_name = Path(parse.urlsplit(post['photo_url']).path).name
    post_image = requests.get(post['photo_url'])
    post_image.raise_for_status()

    file_path = Path.cwd()
    with open(Path.joinpath(file_path, image_file_name), 'wb') as file:
        file.write(post_image.content)

    post_text = sheet_functions.get_post_text(post)
    return post_text, image_file_name


if __name__ == '__main__':
    main()
