from PIL import Image, ImageColor


class Images:
    def __init__(self, config):
        self._config = config

    def fill_with_color(self, image_path: str, image_fit_path: str, image_average_color: str):
        print(f'### [ Resizing ] {image_path} to {image_fit_path} with average color {image_average_color}')

        image = Image.open(image_path)
        image_width, image_height = image.size
        image_fill_color = ImageColor.getrgb(image_average_color)
        new_image = Image.new('RGBA', (self._config.screen_width, self._config.screen_height), image_fill_color)
        new_image.paste(
            image,
            (
                int((self._config.screen_width - image_width) / 2),
                int((self._config.screen_height - image_height) / 2)
            )
        )

        rgb_new_image = new_image.convert('RGB')
        rgb_new_image.save(image_fit_path)
