import json
from pathlib import Path

import gdown
import requests
from bs4 import BeautifulSoup


def download_google_document_text_and_image_url(link_google_document):
    document_name = 'temp_post_file'
    gdown.download(url=link_google_document, output=document_name, fuzzy=True, quiet=True)
    text_with_photo = get_document_text_and_image_url(document_name)
    return text_with_photo


def get_document_text_and_image_url(document):
    with open(document, 'r', encoding='UTF-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        scripts = soup.find_all({'script': 'nonce'})
        for script in scripts:
            if script.text.startswith('DOCS_modelChunk ='):
                docs_model_chunk = script.text.replace('DOCS_modelChunk = ', '')
                excess_chunk_part_char = docs_model_chunk.find('; DOCS_modelChunkLoadStart')
                doc_list = json.loads(docs_model_chunk[:excess_chunk_part_char])

                image_url = get_google_document_image_url(doc_list, scripts)
                post_text = doc_list[0]['s']

                return post_text.replace('*', ''), image_url


def get_google_document_image_url(doc_list, scripts):
    try:
        script_doc_id = doc_list[2]['epm']['ee_eo']['i_cid']
    except KeyError:
        return
    for script in scripts:
        # если здесь добавить пустой список
        if script.text.find(script_doc_id) > 0:
            start_script_doc_id_char = script.text.find(script_doc_id)
            start_script_doc_id = script.text[start_script_doc_id_char:]
            start_image_url_char = start_script_doc_id.find('https')
            start_image_url = start_script_doc_id[start_image_url_char:]
            excess_image_url_char = start_image_url.find('"')
            image_url = start_image_url[:excess_image_url_char]
            # здесь добавлять image_url в список картинок
            return image_url
    # возвращать список картинок после обработки всего цикла


def download_posts_image(image_url):
    try:
        image_file_name = 'image_file.png'
        post_image = requests.get(image_url)
        post_image.raise_for_status()

        file_path = Path.cwd()
        with open(Path.joinpath(file_path, image_file_name), 'wb') as file:
            file.write(post_image.content)
        return image_file_name

    except requests.exceptions.MissingSchema:
        return
