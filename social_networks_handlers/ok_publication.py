import os
from ok_api import OkApi, Upload
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import requests


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


def delet_img(photo_id):
    load_dotenv()
    access_token = os.environ["OK_ACCESS_TOKEN"]
    application_key = os.environ["OK_APPLICATION_KEY"]
    application_secret_key = os.environ["OK_SECRET_KEY"]
    ok_user = os.environ["OK_USER"]

    headers = {'client_id': ok_user}
    params = {
        'scope': 512001823570,
        'access_token': access_token,
        'application_key': application_key,
        'session_secret_key': application_secret_key,
        'response_type': 'token',
        'redirect_uri': 'https://apiok.ru/oauth_callback',
        'photo_id': photo_id,
        'method': 'photos.deletePhoto'
    }
    url_sesion = 'https://api.ok.ru/fb.do'
    response = requests.post(url_sesion, headers=headers, params=params)
    try:
        response.raise_for_status()
        response_message = response.json()
        return True
    except:
        print('Что то опять не так')
        return False


def publication_post_ok(post_text, image_file_name):
    load_dotenv()
    access_token = os.environ["OK_ACCESS_TOKEN"]
    application_key = os.environ["OK_APPLICATION_KEY"]
    application_secret_key = os.environ["OK_SECRET_KEY"]
    album = os.environ["OK_ALBUM"]

    if not image_file_name:
        not_img(post_text)
        image_file_name = 'post.png'

    ok = OkApi(access_token=access_token,
               application_key=application_key,
               application_secret_key=application_secret_key)

    upload = Upload(ok)
    upload_response = upload.photo(photos=[image_file_name], album=album)

    for photo_id in upload_response['photos']:
        token = upload_response['photos'][photo_id]['token']
        response = ok.photosV2.commit(photo_id=photo_id, token=token, comment=post_text)
    try:
        id = response.json()['photos'][0]['photo_id']
        if id:
            return id
    except:
        return None


def main():
    post_text = 'Это сообщение было без картинки'
    image_file_name = ''
    photo_id = publication_post_ok(post_text, image_file_name)
    print(photo_id)
    delet_img(photo_id)


if __name__ == '__main__':
    main()
