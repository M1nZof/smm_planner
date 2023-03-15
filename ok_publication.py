import os
from ok_api import OkApi, Upload
from dotenv import load_dotenv


def main():
    load_dotenv()

    access_token = os.environ["OK_ACCESS_TOKEN"]
    application_key = os.environ["OK_APPLICATION_KEY"]
    application_secret_key = os.environ["OK_SECRET_KEY"]


    ok = OkApi(access_token=access_token,
               application_key=application_key,
               application_secret_key=application_secret_key)

    upload = Upload(ok)
    upload_response = upload.photo(photos=['1.jpg', '2.jpg'])

    for photo_id in upload_response['photos']:
        token = upload_response['photos'][photo_id]['token']
        response = ok.photosV2.commit(photo_id=photo_id, token=token)
        print(response.json())

    print(ok.friends.get())



if __name__ == '__main__':
    main()