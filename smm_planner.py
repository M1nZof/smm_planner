import time
import requests

from urllib import parse
from pathlib import Path

from errors_classes import SocialNetworkError
from google_handlers import sheet_functions, google_document_functions
from social_networks_handlers.ok_publication import publication_post_ok
from social_networks_handlers.tg_publication import send_telegram_post
from social_networks_handlers.vk_publication import publication_post_vk


def main():
    while True:
        all_new_posts = sheet_functions.get_all_new_posts()
        if len(all_new_posts) == 0:
            time.sleep(60)
        else:
            for post in all_new_posts:
                try:
                    post_text, image_url = \
                        google_document_functions.get_google_document_text_and_image_url(post['link_google_document'])
                except requests.exceptions.MissingSchema:
                    continue

                if image_url:
                    image_file_name = download_posts_image_file_name(image_url)
                else:
                    image_file_name = None

                try:
                    if post['Telegram'] == 'TRUE' and\
                            not post['Telegram_result'] or post['Telegram_result'].startswith('Ошибка'):
                        message_id = send_telegram_post(post_text, image_file_name)
                        put_mark(post['row'], 5, message_id)
                    if post['VK'] == 'TRUE' and\
                            not post['VK_result'] or post['VK_result'].startswith('Ошибка'):
                        post_id = publication_post_vk(post_text, image_file_name)
                        put_mark(post['row'], 6, post_id)
                    if post['OK'] == 'TRUE' and\
                            not post['OK_result'] or post['OK_result'].startswith('Ошибка'):
                        post_id = publication_post_ok(post_text, image_file_name)
                        put_mark(post['row'], 7, post_id)

                    if post_text:
                        Path(Path.cwd(), 'temp_post_file').unlink()
                    if image_file_name:
                        Path(Path.joinpath(Path.cwd(), image_file_name)).unlink()

                except SocialNetworkError as error:
                    error_dict = error.__dict__['message']
                    put_mark(post['row'], error_dict['col'], f"Ошибка\n\n{error_dict['message']}", error=True)

                except requests.exceptions.ConnectionError:
                    print(f'Ошибка соединения сети.\nПопытка восстановления соединения...')
                    time.sleep(1)

            time.sleep(3)


def put_mark(row, col, post_result, error=False):
    if not error:
        sheet_functions.format_cell(row, col, sheet_functions.BLACK, sheet_functions.GREEN)
        sheet_functions.post_cell_text(row, col + 3, f'Опубликовано {str(sheet_functions.get_datetime_now())}'
                                                     f'\n\n{post_result}')
    else:
        sheet_functions.format_cell(row, col, sheet_functions.BLACK, sheet_functions.RED)
        sheet_functions.post_cell_text(row, col + 3, str(post_result))


def download_posts_image_file_name(image_url):
    try:
        image_file_name = 'image_file.png'
        post_image = requests.get(image_url)
        post_image.raise_for_status()

        file_path = Path.cwd()
        with open(Path.joinpath(file_path, image_file_name), 'wb') as file:
            file.write(post_image.content)
        return image_file_name

    except requests.exceptions.MissingSchema:
        return


if __name__ == '__main__':
    main()
