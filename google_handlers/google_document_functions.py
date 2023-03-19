import json
from urllib.parse import urlparse

import gdown
from bs4 import BeautifulSoup


def get_post_text(link_google_document):
    document_name = 'temp_post_file'
    gdown.download(url=link_google_document, output=document_name, fuzzy=True, quiet=True)
    text = get_google_document_text(document_name)
    return text


def get_post_image_url(link_google_document):
    document_name = 'temp_post_file'
    gdown.download(url=link_google_document, output=document_name, fuzzy=True, quiet=True)
    image_url = get_google_document_image_url(document_name)
    return image_url


def get_google_document_text(document_name):
    with open(document_name, 'r', encoding='UTF-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        scripts = soup.find_all({'script': 'nonce'})
        text = ''
        for script in scripts:
            if script.text.startswith('DOCS_modelChunk ='):
                text = script.text.replace('DOCS_modelChunk = ', '')
                excess_text_part_char = text.find('; DOCS_modelChunkLoadStart')
                text = text[:excess_text_part_char]
                post_text = json.loads(text)[0]['s']
                break
    return post_text


def get_google_document_image_url(document_name):
    with open(document_name, 'r', encoding='UTF-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        scripts = soup.find_all({'script': 'nonce'})
        text = ''
        for script in scripts:
            if script.text.startswith('DOCS_modelChunk ='):
                text = script.text.replace('DOCS_modelChunk = ', '')
                excess_text_part_char = text.find('; DOCS_modelChunkLoadStart')
                text = text[:excess_text_part_char]
                text2 = json.loads(text)[2]['epm']['ee_eo']['i_cid']
                break
        for script in scripts:
            if script.text.find(text2) > 0:
                start_text_part_char = script.text.find(text2)
                text3 = script.text[start_text_part_char:]
                start_text_part_char = text3.find('":"')
                text3 = text3[start_text_part_char:]
                excess_text_part_char = text3.find('"}')
                image_url = text3[3:excess_text_part_char]
                break
    return image_url
