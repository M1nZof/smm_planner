import time
import requests

from pathlib import Path

from error_classes.errors_classes import SocialNetworkError
from google_handlers import sheet_functions
from google_handlers.google_document_functions import\
    download_posts_image, \
    download_google_document_text_and_image_url
from google_handlers.sheet_functions import put_mark
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
                print(post)
                try:
                    post_text, image_url = \
                        download_google_document_text_and_image_url(post['link_google_document'])
                except requests.exceptions.MissingSchema:
                    continue

                if image_url:
                    image_file_name = download_posts_image(image_url)
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
                    for _ in range(10):
                        print(f'Ошибка соединения сети.\nПопытка восстановления соединения...')
                        time.sleep(1)
                    time.sleep(60)

            time.sleep(3)


if __name__ == '__main__':
    main()
