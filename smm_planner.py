import sys
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
        datetime_now = sheet_functions.get_datetime_now()
        for post_number, post in enumerate(all_new_posts):
            formatted_datetime = sheet_functions.get_formatted_datetime(post['date'], post['time'])
            if not formatted_datetime <= datetime_now:
                break
            post_text, image_file_name = get_posts_text_imagefile(post)
            # TODO лучше разбить получение фото и текста на разные функции
            cell = sheet_functions.WORKSHEET.find(post['link_google_document'])
            # TODO вместо поиска лучше как-то передавать с публикацией поста номера столбца и строки. Я еще подумаю
            try:
                if post['Telegram'] == 'TRUE' and not post['Telegram_rez']:
                    # TODO в будущем переименовать на нормальное значение ("rez" - типо результат? :/)
                    message_id = send_telegram_post(post_text, image_file_name)
                    put_mark(cell.row, 5, message_id)
                if post['VK'] == 'TRUE' and not post['VK_rez']:
                    post_id = publication_post_vk(post_text, image_file_name)
                    put_mark(cell.row, 6, post_id)
                if post['OK'] == 'TRUE' and not post['OK_rez']:
                    post_id = publication_post_ok(post_text, image_file_name)
                    put_mark(cell.row, 7, post_id)

            except SocialNetworkError as error:
                put_mark(cell.row, 5, error)                # TODO check col. Проблема, описанная выше

            except requests.exceptions.HTTPError as error:
                put_mark(cell.row, 5, error)                # TODO check col. Проблема, описанная выше

                # sys.exit(f"Ошибка сети")          # Здесь может быть другая обработка. Я не придумал другой. Просто
                #                                   # пишу в ячейку, что она есть

            except requests.exceptions.ConnectionError:
                print(f'Ошибка соединения сети.\nПопытка восстановления соединения...')
                time.sleep(1)

            Path(Path.cwd(), 'temp_post_file').unlink()  # удаляем этот временный файл с html поста
            Path(Path.joinpath(Path.cwd(), image_file_name)).unlink()  # удаляем файл изображения

        time.sleep(3)  # ограничение запроса к Гуглу, иначе блокирует доступ
# https://stackoverflow.com/questions/65153922/why-am-i-receiving-a-quota-limit-error-google-cloud-platform-compute-engine-vm


def put_mark(row, col, post_result):
    if isinstance(post_result, (str, int, list)):
        # Если пришла строка или число, то пост опубликован, иначе это ошибка
        # P.S. Список кидается в случае, если опубликовано 2 поста в телегу (из-за лимита символов)
        sheet_functions.format_cell(row, col, sheet_functions.BLACK, sheet_functions.GREEN)
        sheet_functions.post_cell_text(row, col + 3, f'Опубликовано {str(sheet_functions.get_datetime_now())}'
                                                     f'\n\n{post_result}')
    else:
        sheet_functions.format_cell(row, col, sheet_functions.BLACK, sheet_functions.RED)
        sheet_functions.post_cell_text(row, col + 3, str(post_result))


def get_posts_text_imagefile(post):
    image_file_name = f'image_file{Path(parse.urlsplit(post["photo_url"]).path).suffix}'
    post_image = requests.get(post['photo_url'])
    post_image.raise_for_status()

    file_path = Path.cwd()
    with open(Path.joinpath(file_path, image_file_name), 'wb') as file:
        file.write(post_image.content)

    post_text = google_document_functions.get_post_text(post['link_google_document'])
    return post_text, image_file_name


if __name__ == '__main__':
    main()
