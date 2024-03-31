#!/usr/bin/env python3

import os
import random
import shutil
import urllib.parse

import cv2
import requests
from PIL import Image, ImageColor

from config.Config import Config

_config = Config.instance()


def __escape(value: str) -> str:
    return urllib.parse.quote(value)


def __normalize_url(path: str, parameters: dict[str, str], quote_parameters: bool = True) -> str:
    _parameters = parameters

    __parameters = {k: __escape(v) if quote_parameters else v for k, v in _parameters.items()}
    __parameters_string = '&'.join([f'{key}={value}' for key, value in __parameters.items()])

    return f'{path}?{__parameters_string}'


def __normalize_headers(headers: dict[str, str]) -> dict[str, str]:
    headers[_config.rest_header_authorization_key] = _config.account_api_key
    return headers


def __get_response(path: str, parameters: dict[str, str] = {}, headers: dict[str, str] = {}):
    try:
        response = requests.get(
            url=__normalize_url(path, parameters),
            headers=__normalize_headers(headers),
            timeout=1000
        )

        if not response.ok:
            print(f'### [ Request ] Failed :: Raw response :: {response.text}')

        response.raise_for_status()

        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)


def __persist_url(remote, local):
    print(f'### [ Saving ] {remote} to {local}')

    r = requests.get(remote, headers=__normalize_headers({}), stream=True)
    with open(local, "wb") as out_file:
        shutil.copyfileobj(r.raw, out_file)


def __fit_persisted_file(image_path, image_fit_path, image_average_color):
    print(f'### [ Resizing ] {image_path} to {image_fit_path} with average color {image_average_color}')

    image = Image.open(image_path)
    image_width, image_height = image.size
    image_fill_color = ImageColor.getrgb(image_average_color)
    new_image = Image.new('RGBA', (_config.screen_width, _config.screen_height), image_fill_color)
    new_image.paste(image, (int((_config.screen_width - image_width) / 2), int((_config.screen_height - image_height) / 2)))

    rgb_new_image = new_image.convert('RGB')
    rgb_new_image.save(image_fit_path)


def __show_full_screen_image(image_fit_path):
    final_image = cv2.imread(image_fit_path)
    cv2.namedWindow("Pexels Preview", cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty("Pexels Preview", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Pexels Preview", final_image)

    key = cv2.waitKey(_config.behaviour_slide_duration)

    if key == 27:
        return True
    else:
        return False


if __name__ == '__main__':
    genres = _config.genres_favourites
    if _config.behaviour_randomise_genres:
        random.shuffle(genres)
    items_from_genres = _config.behaviour_max_slides_from_genre
    rest_query_genre = _config.rest_query_genre
    rest_full_image_suffix = _config.rest_full_image_suffix
    cache_local_path = _config.cache_local_path
    cache_fit_local_path = _config.cache_fit_local_path
    key_genre = _config.keys_genre
    keys_width = _config.keys_width
    keys_height = _config.keys_height
    keys_id = _config.keys_id
    width = _config.screen_width
    height = _config.screen_height

    genre_index = 0
    genres_length = len(genres)

    while True:
        genre = genres[genre_index]
        print(f'### [ Genre ] start with {genre}')

        response = __get_response(rest_query_genre.replace(key_genre, genre))
        images = response['photos']
        image_index = 0
        image_index_global = 0
        images_length = len(images)

        while image_index_global < items_from_genres:
            print(f'### [ {genre} ] opening {image_index_global} :: {image_index} from {items_from_genres} :: {images_length}')
            if image_index < images_length:
                image = images[image_index]
                image_id = image['id']
                image_width = image['width']
                image_height = image['height']
                image_average_color = image['avg_color'] if _config.behaviour_use_average_color else _config.behaviour_fallback_fill_color

                if image_width > image_height:
                    desired_width = width
                    desired_height = desired_width * image_height / image_width
                else:
                    desired_height = height
                    desired_width = desired_height * image_width / image_height

                source = image['src']['original'] + rest_full_image_suffix \
                    .replace(keys_width, str(desired_width)) \
                    .replace(keys_height, str(desired_height))
                image_index = image_index + 1
                image_index_global = image_index_global + 1

                destination = cache_local_path.replace(keys_id, str(image_id))
                fit_destination = cache_fit_local_path.replace(keys_id, str(image_id))

                if not os.path.exists(destination):
                    __persist_url(source, destination)
                    __fit_persisted_file(destination, fit_destination, image_average_color)

                if __show_full_screen_image(fit_destination):
                    exit(1)
            elif 'next_page' in response:
                print(f'### [ {genre} ] loading next page')
                response = __get_response(response['next_page'], {}, {})
                images = response['photos']
                image_index = 0
                images_length = len(images)
            else:
                print(f'### [ {genre} ] nothing more to load, proceeding to the next one')
                image_index_global = items_from_genres

        genre_index = genre_index + 1
        if genre_index > genres_length:
            genre_index = 0
