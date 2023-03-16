import os
from ok_api import OkApi, Upload
from dotenv import load_dotenv


def publication_post_ok(post_text, image_file_name):
    load_dotenv()
    access_token = os.environ["OK_ACCESS_TOKEN"]
    application_key = os.environ["OK_APPLICATION_KEY"]
    application_secret_key = os.environ["OK_SECRET_KEY"]
    album = os.environ["OK_ALBUM"]

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
    image_file_name = '2.jpg'
    luck = publication_post_ok(post_text, image_file_name)


if __name__ == '__main__':
    main()
