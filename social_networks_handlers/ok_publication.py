import requests

from ok_api import OkApi, Upload, ok_exceptions
from environs import Env
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from error_classes.errors_classes import SocialNetworkError


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


def convert_text_to_picture(text, image_file_name):
    img = Image.new('RGBA', (600, 400), 'white')
    ImageDraw.Draw(img)
    img.save(image_file_name)
    image = Image.open(image_file_name)
    image_draw = ImageDraw.Draw(image)
    black = (240, 8, 12)
    font = ImageFont.truetype(str(Path.joinpath(Path.cwd(), 'social_networks_handlers', 'FreeMono.ttf')), size=18)
    line_number = 30

    for x in range(0, len(text), 50):
        image_draw.text((10, line_number), (text[x:x + 50]), fill=black, font=font, color='red')
        line_number = line_number + 30

    image.save(image_file_name)

    return image_file_name


def publication_post_ok(post_text, image_file_name):
    access_token, application_key, application_secret_key, ok_user, ok_application_id, album = get_ok_environs()
    post_text = post_text[:255]

    if not image_file_name:
        image_file_name = convert_text_to_picture(post_text, 'post.png')

    ok = OkApi(access_token=access_token,
               application_key=application_key,
               application_secret_key=application_secret_key)
    upload = Upload(ok)

    try:
        upload_response = upload.photo(photos=[image_file_name], album=album)
        for photo_id in upload_response['photos']:
            token = upload_response['photos'][photo_id]['token']
            response = ok.photosV2.commit(photo_id=photo_id, token=token, comment=post_text)

            try:
                photo_id = response.json()['photos'][0]['photo_id']
            except KeyError:
                raise SocialNetworkError({'col': 7, 'message': response.json()['error_msg']})

        if image_file_name == 'post.png':
            Path(Path.cwd(), image_file_name).unlink()

        return photo_id

    except ok_exceptions.OkApiException as error:
        raise SocialNetworkError({'col': 7, 'message': error.__dict__['message']['error_msg']})

    except requests.exceptions.HTTPError:
        raise SocialNetworkError({'col': 7, 'message': 'HTTPError'})

    except requests.exceptions.ConnectionError:
        raise requests.exceptions.ConnectionError
