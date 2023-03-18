from ok_api import OkApi, Upload
from environs import Env
from PIL import Image, ImageDraw, ImageFont
import requests


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


def not_img(text):
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
        not_img(post_text)
        image_file_name = 'post.png'
    ok = OkApi(access_token=access_token,
               application_key=application_key,
               application_secret_key=application_secret_key)
    upload = Upload(ok)
    
    try:
        upload_response = upload.photo(photos=[image_file_name], album=album)
        except:
        return False, 'Такого Альбома в ОК нет, либо у Вас нет прав'
    
    for photo_id in upload_response['photos']:
        token = upload_response['photos'][photo_id]['token']
        response = ok.photosV2.commit(photo_id=photo_id, token=token, comment=post_text)
    try:
        img_id = response.json()['photos'][0]['photo_id']
        if img_id:
            return img_id
    except:
        return False, 'Ошибка выгрузки'
