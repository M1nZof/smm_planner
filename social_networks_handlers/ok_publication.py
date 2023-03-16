import os
from ok_api import OkApi, Upload
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import sys

def not_img(post_text):
    img = Image.new('RGBA', (200, 200), 'white')
    idraw = ImageDraw.Draw(img)
    img.save('post.png')
    image = Image.open('post.png')
    idraw = ImageDraw.Draw(image)

    font = ImageFont.truetype('FreeMono.ttf', size=18)
    idraw.text((10, 10), post_text, font=font, color='red')
    image.save('post.png')


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
        if response.json()['photos'][0]['status'] == 'SUCCESS':
            return True
    except:
        return False


def main():
    post_text = 'Какая то бабуйня в космосе'
    image_file_name = ''
    luck = publication_post_ok(post_text, image_file_name)


if __name__ == '__main__':
    main()
