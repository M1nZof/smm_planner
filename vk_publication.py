import requests
from urllib import parse
from urllib.error import HTTPError
from pathlib import Path
from environs import Env
from random import randint


def check_vk_request_error(response):
    error_code = 0
    if 'error' in response:
        error_message = response['error']['error_msg']
        if response['error']['error_code']:
            error_code = response['error']['error_code']
        raise HTTPError('Ошибка сервиса ВКонтакте', error_code, error_message, error_message, None)


def get_photos_wall_upload_server(vk_access, vk_group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'group_id': vk_group_id,
        'v': 5.131,
    }
    response = requests.get(url, headers=vk_access, params=payload)
    response.raise_for_status()
    response = response.json()
    check_vk_request_error(response)
    return response['response']['album_id'], response['response']['upload_url']


def save_photo_to_wall(vk_access, vk_group_id, upload_url, file_path, post_file_name):
    with open(Path.joinpath(file_path, post_file_name), 'rb') as photo:
        response = requests.post(upload_url, files={'photo': photo})
    response.raise_for_status()
    transfer_file_params = response.json()

    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {
        'group_id': vk_group_id,
        'server': transfer_file_params['server'],
        'photo': transfer_file_params['photo'],
        'hash': transfer_file_params['hash'],
        'v': 5.131,
    }
    response = requests.get(url, headers=vk_access, params=payload)
    response.raise_for_status()
    photo_parameters = response.json()
    check_vk_request_error(photo_parameters)
    photo_owner_id = photo_parameters['response'][0]['owner_id']
    photo_id = photo_parameters['response'][0]['id']
    return photo_owner_id, photo_id


def post_wall_photo(vk_access, vk_group_id, post_alt, photo_owner_id, photo_id):
    url = 'https://api.vk.com/method/wall.post'
    payload = {
        'attachments': f"photo{photo_owner_id}_{photo_id}",
        'owner_id': int(f'-{vk_group_id}'),
        'from_group': 1,
        'message': post_alt,
        'v': 5.131,
    }
    response = requests.post(url, headers=vk_access, params=payload)
    response.raise_for_status()
    response = response.json()
    check_vk_request_error(response)


def get_random_post():
    last_post = requests.get(f'{POST_LINK}/info.0.json')
    last_post.raise_for_status()
    last_post_id = last_post.json()['num']

    random_post_id = randint(1, last_post_id)

    post_parameters = requests.get(f'{POST_LINK}{str(random_post_id)}/info.0.json')
    post_parameters.raise_for_status()
    post_parameters = post_parameters.json()

    post = requests.get(post_parameters['img'])
    post.raise_for_status()

    return post_parameters, post, random_post_id


def main():
    env = Env()
    env.read_env()
    vk_access_token = env.str('VK_ACCESS_TOKEN')
    vk_group_id = env.int('VK_GROUP_ID')
    vk_authorization = {'Authorization': f'Bearer {vk_access_token}'}

    file_path = Path.cwd()
    Path(file_path).mkdir(parents=True, exist_ok=True)

    post_parameters, post, random_post_id = get_random_post()
    post_file_name = Path(parse.urlsplit(post_parameters['img']).path).name

    try:
        with open(Path.joinpath(file_path, post_file_name), 'wb') as file:
            file.write(post.content)
        print(f'Публикуем комикс № {random_post_id}')
        album_id, upload_url = get_photos_wall_upload_server(vk_authorization, vk_group_id)
        photo_owner_id, photo_id = save_photo_to_wall(vk_authorization, vk_group_id, upload_url, file_path, post_file_name)
        post_wall_photo(vk_authorization, vk_group_id, post_parameters['alt'], photo_owner_id, photo_id)
    except requests.exceptions.HTTPError as error:
        print(f'Ошибка сети.\nОшибка {error}')
    finally:
        Path(Path.joinpath(file_path, post_file_name)).unlink()


if __name__ == "__main__":
    main()
