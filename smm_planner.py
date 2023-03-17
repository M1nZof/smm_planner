import time
from urllib import parse

import requests
from environs import Env

from google_handlers import sheet_functions

from pathlib import Path

from google_handlers.google_document_functions import get_post_text
from social_networks_handlers.ok_publication import publication_post_ok
from social_networks_handlers.tg_publication import send_telegram_post, get_telegram_message_id, delete_telegram_post
from social_networks_handlers.vk_publication import publication_post_vk


def main():
    env = Env()
    env.read_env()

    while True:
        all_new_posts = sheet_functions.get_all_new_posts()

        max_quantity_of_requests = 5  # задумка увеличить число запросов до +- разумного уровня,
                                      # чтобы не морозить код слишком часто.
                                      # Профит в том, что мы будем обрабатывать посты раз в ~час, но полноценно,
                                      # с удалениями старых постов, добавлениями нужных по сроку других постов.
                                      # Открыто для обсуждения и совершествования. Сейчас - сугубо прототип, чтобы
                                      # вы поняли задумку

        if len(all_new_posts) > 0:
            for post_number, post in enumerate(all_new_posts, start=1):
                if post_number <= max_quantity_of_requests:
                    if post['duration'] and post['public_fact']:
                        message_id = post['public_fact'].split('\n')[1]
                        if message_id != 'Был удален':
                            delete_telegram_post(message_id)
                            cell = sheet_functions.WORKSHEET.find(post['link_google_document'])
                            sheet_functions.post_cell_text(cell.row, 7, f'{str(sheet_functions.get_datetime_now())}'
                                                                        f'\nБыл удален')

                    post_text = get_post_text(post['link_google_document'])
                    image_file_name = get_posts_imagefile(post)

                    if not post['public_fact']:
                        if post['social_network'] == 'Telegram':
                            message = send_telegram_post(post_text, image_file_name)
                            post_id = get_telegram_message_id(message)
                        elif post['social_network'] == 'VK':
                            publication_post_vk(post_text, image_file_name)
                        elif post['social_network'] == 'OK':
                            publication_post_ok(post_text, image_file_name)
                        cell = sheet_functions.WORKSHEET.find(post['link_google_document'])
                        if isinstance(post_id, list):
                            sheet_functions.post_cell_text(cell.row, 7,
                                                           f'{str(sheet_functions.get_datetime_now())}'
                                                           f'\n{post_id[0]}, {post_id[1]}')
                        else:
                            sheet_functions.post_cell_text(cell.row, 7,
                                                           f'{str(sheet_functions.get_datetime_now())}'
                                                           f'\n{post_id}')
                        Path(Path.cwd(), 'temp_post_file').unlink()  # удаляем этот временный файл с html поста
                        Path(Path.joinpath(Path.cwd(), image_file_name)).unlink()  # удаляем файл изображения
                else:
                    time.sleep(60)


def get_posts_imagefile(post):
    image_file_name = Path(parse.urlsplit(post['photo_url']).path).name
    post_image = requests.get(post['photo_url'])
    post_image.raise_for_status()

    file_path = Path.cwd()
    with open(Path.joinpath(file_path, image_file_name), 'wb') as file:
        file.write(post_image.content)

    return image_file_name


if __name__ == '__main__':
    main()
