import time
from urllib import parse

import requests

from google_handlers import sheet_functions

from pathlib import Path

from social_networks_handlers.ok_publication import publication_post_ok
from social_networks_handlers.tg_publication import send_telegram_post
from social_networks_handlers.vk_publication import publication_post_vk
from social_networks_handlers.vk_publication import delete_post_vk


def main():
    while True:
        all_new_posts = sheet_functions.get_all_new_posts()
        for post_number, post in enumerate(all_new_posts):
            post_text, image_file_name = get_posts_text_imagefile(post)
            if post['social_network'] == 'Telegram':
                send_telegram_post(post_text, image_file_name)
            elif post['social_network'] == 'VK':
                publication_post_vk(post_text, image_file_name)
            elif post['social_network'] == 'OK':
                publication_post_ok(post_text, image_file_name)

                cell = sheet_functions.WORKSHEET.find(post['link_google_document'])
                sheet_functions.post_cell_text(cell.row, 7, str(sheet_functions.get_datetime_now()))
                time.sleep(3)

                Path(Path.cwd(), 'temp_post_file').unlink()  # удаляем этот временный файл с html поста
                Path(Path.joinpath(Path.cwd(), image_file_name)).unlink()  # удаляем файл изображения

        time.sleep(30)  # ограничение запроса к Гуглу, иначе блокирует доступ
# https://stackoverflow.com/questions/65153922/why-am-i-receiving-a-quota-limit-error-google-cloud-platform-compute-engine-vm


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
