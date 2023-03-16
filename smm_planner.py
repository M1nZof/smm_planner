from urllib import parse

import requests

from google_handlers import sheet_functions

from pathlib import Path
from environs import Env

from social_networks_handlers import vk_publication, ok_publication, tg_publication


def main():
    env = Env()
    env.read_env()

    # всего постов
    posts_count = sheet_functions.get_posts_count()

    all_new_posts = sheet_functions.get_all_new_posts()
    for post in all_new_posts:
        # получаем текст поста и имя файла картинки
        post_text, image_file_name = get_posts_text_imagefile(post)

        # публикуем пост Вконтаке
        vk_publication.publication_post_vk(post_text, image_file_name)

        # публикуем пост в Одноклассниках
        ok_publication.publication_post_ok(post_text, image_file_name)

        # публикуем пост в Telegram
        # tg_publication.send_telegram_post(telegram_bot_token, telegram_chat_id, post_text, image_file_name)


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
