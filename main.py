import sheet_functions
import requests


from pathlib import Path
from environs import Env
from urllib import parse


import vk_publication


def main():
    env = Env()
    env.read_env()

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


def get_posts_text_imagefile(post_number):
    all_posts = sheet_functions.get_all_records()
    post = all_posts[post_number-1]
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
