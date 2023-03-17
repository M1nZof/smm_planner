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
            formatted_datetime = sheet_functions.get_formatted_datetime(post['date'], post['time'])
            datetime_now = sheet_functions.get_datetime_now()
            if formatted_datetime <= datetime_now:
                post_text, image_file_name = get_posts_text_imagefile(post)
                if post['social_network'] == 'Telegram':
                    post_result = send_telegram_post(post)
                elif post['social_network'] == 'VK':
                    post_result = publication_post_vk(post_text, image_file_name)
                elif post['social_network'] == 'OK':
                    post_result = publication_post_ok(post_text, image_file_name)

                cell = sheet_functions.WORKSHEET.find(post['link_google_document'])
                if post_result:
                    sheet_functions.format_cell(cell.row, 7, sheet_functions.GREEN, sheet_functions.BLACK)
                    sheet_functions.post_cell_text(cell.row, 7, f'Опубликован {str(sheet_functions.get_datetime_now())}')
                else:
                    sheet_functions.format_cell(cell.row, 7, sheet_functions.RED, sheet_functions.GREEN)
                    sheet_functions.post_cell_text(cell.row, 7, 'Ошибка публикации')

                time.sleep(3)

                Path(Path.cwd(), 'temp_post_file').unlink()  # удаляем этот временный файл с html поста
                Path(Path.joinpath(Path.cwd(), image_file_name)).unlink()  # удаляем файл изображения

        time.sleep(30)  # ограничение запроса к Гуглу, иначе блокирует доступ
# https://stackoverflow.com/questions/65153922/why-am-i-receiving-a-quota-limit-error-google-cloud-platform-compute-engine-vm


def get_posts_text_imagefile(post):
    image_file_name = f'image_file{Path(parse.urlsplit(post["photo_url"]).path).suffix}'
    post_image = requests.get(post['photo_url'])
    post_image.raise_for_status()

    file_path = Path.cwd()
    with open(Path.joinpath(file_path, image_file_name), 'wb') as file:
        file.write(post_image.content)

    post_text = sheet_functions.get_post_text(post)
    return post_text, image_file_name


if __name__ == '__main__':
    main()
