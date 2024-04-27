import copy
import os
import random
import time
from enum import Enum
from threading import Event

import cv2
from PIL import UnidentifiedImageError

from tools.Images import Images
from tools.RestApi import RestApi


class Action(Enum):
    LOAD_GENRE = 'load_genre'
    LOAD_IMAGE = 'load_image'
    CHANGE_TIME = 'change_time'
    EXIT = 'exit'
    NOTHING = None


class Runner:
    def __init__(self, config):
        self._config = config
        self._stop_event = Event()

        self._api = RestApi(config)
        self._images = Images(config)

        self._action = Action.LOAD_GENRE

        self._current_genres = config.genres_favourites
        if config.behaviour_randomise_genres:
            random.shuffle(self._current_genres)
        self._current_genre_response = None
        self._current_genre_index = 0
        self._current_images = []
        self._current_image_index = 0
        self._current_image_genre_index = 0
        self._current_image = None
        self._current_image_set_at = None
        self._current_time = None

    def start(self):
        self.run()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            action = self._get_next_action()
            if action is not Action.NOTHING:
                print(f'### [ Runner ] handling {action}')

            if action == Action.LOAD_GENRE:
                self._load_genre()
            elif action == Action.LOAD_IMAGE:
                self._load_image()
            elif action == Action.CHANGE_TIME:
                self._change_time()
            elif action == Action.EXIT:
                self.stop()

            if not self._check_for_escape() and action == Action.NOTHING:
                if (time.time() - self._current_image_set_at) >= self._config.behaviour_slide_duration:
                    self._action = Action.LOAD_IMAGE
                elif self._config.watch_enabled and (self._current_time != self._get_time_as_string()):
                    self._action = Action.CHANGE_TIME

    def _load_genre(self):
        genre = self._current_genres[self._current_genre_index]
        print(f'### [ Genre ] start with {genre}')

        self._current_genre_response = self._api.get_json(
            self._config.rest_query_genre.replace(self._config.keys_genre, genre)
        )
        self._current_images = self._current_genre_response['photos']
        self._current_image_index = 0
        self._current_image_genre_index = 0

        self._current_genre_index = self._current_genre_index + 1
        if self._current_genre_index >= len(self._current_genres):
            self._current_genre_index = 0

        self._action = Action.LOAD_IMAGE

    def _load_image(self):
        config = self._config
        print(
            f'### [ {self._current_genres[self._current_genre_index]} ]'
            f' opening {self._current_image_index} / {len(self._current_images)}'
            f' :: {self._current_image_genre_index} / {config.behaviour_max_slides_from_genre}'
        )

        if self._current_image_genre_index >= config.behaviour_max_slides_from_genre:
            self._action = Action.LOAD_GENRE
        elif len(self._current_images) == 0:
            self._action = Action.LOAD_GENRE
        elif (self._current_image_index >= len(self._current_images)) and ('next_page' not in self._current_genre_response):
            self._action = Action.LOAD_GENRE
        elif (self._current_image_index >= len(self._current_images)) and ('next_page' in self._current_genre_response):
            print(f'### [ {self._current_genres[self._current_genre_index]} ] loading next page')
            self._current_genre_response = self._api.get_json(self._current_genre_response['next_page'])
            self._current_images = self._current_genre_response['photos']
            self._current_image_index = 0

            self._load_image()
        else:
            image = self._current_images[self._current_image_index]
            image_id = image['id']
            image_width = image['width']
            image_height = image['height']
            image_average_color = image['avg_color'] if config.behaviour_use_average_color else config.behaviour_fallback_fill_color

            if image_width > image_height:
                desired_width = config.screen_width
                desired_height = desired_width * image_height / image_width
            else:
                desired_height = config.screen_height
                desired_width = desired_height * image_width / image_height

            source = image['src']['original'] + config.rest_full_image_suffix \
                .replace(config.keys_width, str(desired_width)) \
                .replace(config.keys_height, str(desired_height))
            destination = config.cache_local_path.replace(config.keys_id, str(image_id))
            fit_destination = config.cache_fit_local_path.replace(config.keys_id, str(image_id))

            try:
                if not os.path.exists(destination):
                    self._api.persist(source, destination)
                if not os.path.exists(fit_destination):
                    self._images.fill_with_color(destination, fit_destination, image_average_color)
            except UnidentifiedImageError:
                print(f'### [ Runner ] image handling failed, removing local cache and trying again')

                try:
                    os.remove(destination)
                except OSError:
                    pass

                try:
                    os.remove(fit_destination)
                except OSError:
                    pass

                self._action = Action.LOAD_IMAGE
                return None

            self._show_full_screen_image(fit_destination)

            self._current_image_index = self._current_image_index + 1
            self._current_image_genre_index = self._current_image_genre_index + 1

    def _change_time(self):
        self._show_image()

    def _check_for_escape(self):
        key = cv2.waitKey(1000)
        if key == 27:
            self._action = Action.EXIT
            return True
        elif key != -1:
            self._action = Action.LOAD_IMAGE
            return True
        else:
            return False

    def _show_full_screen_image(self, image_fit_path):
        self._current_image = cv2.imread(image_fit_path)
        self._current_image_set_at = time.time()
        self._show_image()

    def _add_time_to_current_image(self):
        if self._current_image is not None:
            image = copy.copy(self._current_image)

            screen_width = self._config.screen_width
            screen_height = self._config.screen_height
            random_offset_jump = random.randint(
                -self._config.watch_max_random_offset_jump,
                self._config.watch_max_random_offset_jump
            )
            screen_offset_x = self._config.watch_offset_bottom_right_x + random_offset_jump
            screen_offset_y = self._config.watch_offset_bottom_right_y + random_offset_jump
            position_gray = (
                screen_width - screen_offset_x - self._config.watch_offset_shadow,
                screen_height - screen_offset_y - self._config.watch_offset_shadow
            )
            position_white = (
                screen_width - screen_offset_x,
                screen_height - screen_offset_y
            )

            self._current_time = self._get_time_as_string()
            image = cv2.putText(
                image, self._current_time, position_gray, cv2.FONT_HERSHEY_SIMPLEX,
                self._config.watch_font_scale, (128, 128, 128), self._config.watch_font_thickness, cv2.LINE_AA
            )
            image = cv2.putText(
                image, self._current_time, position_white, cv2.FONT_HERSHEY_SIMPLEX,
                self._config.watch_font_scale, (255, 255, 255), self._config.watch_font_thickness, cv2.LINE_AA
            )

            return image
        else:
            return None

    def _get_time_as_string(self):
        return time.strftime("%H:%M")

    def _show_image(self):
        image = self._add_time_to_current_image() if self._config.watch_enabled else self._current_image
        if image is not None:
            # cv2.destroyWindow("Pexels Preview")

            cv2.namedWindow("Pexels Preview", cv2.WINDOW_FULLSCREEN)
            cv2.setWindowProperty("Pexels Preview", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Pexels Preview", image)

    def _get_next_action(self):
        action = self._action
        self._action = Action.NOTHING
        return action
