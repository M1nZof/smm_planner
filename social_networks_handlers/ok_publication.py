import requests

from ok_api import OkApi, Upload, ok_exceptions
from environs import Env
from PIL import Image, ImageDraw, ImageFont

from errors_classes import SocialNetworkError


def get_ok_environs():
    env = Env()
    env.read_env()
    access_token = env("OK_ACCESS_TOKEN")
    application_key = env("OK_APPLICATION_KEY")
    application_secret_key = env("OK_SECRET_KEY")
    ok_user = env("OK_USER")
    ok_application_id = env("OK_APPLICATION_ID")
    album = env("OK_ALBUM")
    return access_token, application_key, application_secret_key, ok_user, ok_application_id, album


def convert_text_to_picture(text):      # Переименовал функцию. Просто звучнее как-то в логике кода смотрится
    img = Image.new('RGBA', (600, 400), 'white')
    idraw = ImageDraw.Draw(img)
    img.save('post.png')
    image = Image.open('post.png')
    idraw = ImageDraw.Draw(image)
    black = (240, 8, 12)
    font = ImageFont.truetype('FreeMono.ttf', size=18)
    idraw.text((10, 30), text, fill=black, font=font, color='red')
    image.save('post.png')


def publication_post_ok(post_text, image_file_name):
    access_token, application_key, application_secret_key, ok_user, ok_application_id, album = get_ok_environs()
    if not image_file_name:
        convert_text_to_picture(post_text)
        image_file_name = 'post.png'
    ok = OkApi(access_token=access_token,
               application_key=application_key,
               application_secret_key=application_secret_key)
    upload = Upload(ok)

    try:
        upload_response = upload.photo(photos=[image_file_name], album=album)
        for photo_id in upload_response['photos']:
            token = upload_response['photos'][photo_id]['token']
            response = ok.photosV2.commit(photo_id=photo_id, token=token, comment=post_text)
            # TODO здесь лучше ловить ответ от ОК по аналогии с вк, т.к., например, слишком длинные сообщения не хотят
            #  кидаться, но исключения нет, а только тот же response. Если будет реализовано, то проблема ниже
            #  будет решена
            photo_id = response.json()['photos'][0]['photo_id']
            return photo_id

    except ok_exceptions.OkApiException as error:
        # Странно, но иногда кидаются исключения, а иногда возвращается response как будто все ОК
        raise SocialNetworkError(error.__dict__['message']['error_msg'])

    except requests.exceptions.HTTPError:
        raise requests.exceptions.HTTPError

    except requests.exceptions.ConnectionError:
        raise requests.exceptions.ConnectionError

    except KeyError:
        # Здесь я не придумал какую лучше ошибку ловить. Можно пробовать поднимать кастомную, если в response
        # есть ['error_msg']. Оставил пока так, чтобы обсудить
        raise SocialNetworkError(response.json()['error_msg'])
