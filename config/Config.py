import configparser


class Config:
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)

            config = configparser.ConfigParser()
            config.read('config/config.ini')

            cls._instance.account_api_key = config['ACCOUNT']['api_key']

            cls._instance.screen_width = int(config['SCREEN']['width'])
            cls._instance.screen_height = int(config['SCREEN']['height'])

            cls._instance.behaviour_slide_duration = int(config['BEHAVIOUR']['slide_duration'])
            cls._instance.behaviour_max_slides_from_genre = int(config['BEHAVIOUR']['max_slides_from_genre'])
            cls._instance.behaviour_randomise_genres = True if config['BEHAVIOUR']['randomise_genres'].strip().lower() == 'true' else False
            cls._instance.behaviour_use_average_color = True if config['BEHAVIOUR']['use_average_color'].strip().lower() == 'true' else False
            cls._instance.behaviour_fallback_fill_color = config['BEHAVIOUR']['fallback_fill_color']

            cls._instance.genres_favourites = list(map(str.strip, config['GENRES']['favourites'].split(',')))

            cls._instance.watch_font_scale = float(config['WATCH']['font_scale'])
            cls._instance.watch_font_thickness = int(config['WATCH']['font_thickness'])
            cls._instance.watch_offset_bottom_right_x = int(config['WATCH']['offset_bottom_right_x'])
            cls._instance.watch_offset_bottom_right_y = int(config['WATCH']['offset_bottom_right_y'])
            cls._instance.watch_offset_shadow = int(config['WATCH']['offset_shadow'])
            cls._instance.watch_max_random_offset_jump = int(config['WATCH']['max_random_offset_jump'])

            cls._instance.keys_genre = config['KEYS']['genre']
            cls._instance.keys_width = config['KEYS']['width']
            cls._instance.keys_height = config['KEYS']['height']
            cls._instance.keys_id = config['KEYS']['id']

            cls._instance.rest_header_authorization_key = config['REST']['header_authorization_key']
            cls._instance.rest_query_genre = config['REST']['query_genre']
            cls._instance.rest_full_image_suffix = config['REST']['full_image_suffix']

            cls._instance.cache_local_path = config['CACHE']['local_path']
            cls._instance.cache_fit_local_path = config['CACHE']['fit_local_path']

        return cls._instance
