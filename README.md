# pexels.com Screensaver

Pexels.com screensaver

Simple screensavers based on pexels.com Rest Api

## Getting started

- Copy `config/config.ini.default` to `config/config.ini`

- Fill in your credentials in the file
```
[ACCOUNT]
api_key = <your api key>
```

- Change your screen (preferred) width and height
```
[SCREEN]
width = 1920
height = 1080
```

- Adjust how long each slide shall stay and how many items per genre you prefer

`slide_duration` is in seconds

`max_slides_from_genre` will define how many images to play from one genre before moving to the next one
```
slide_duration = 15
max_slides_from_genre = 50
```

- Adjust your preferred genres

Values are csv - space after coma is not required
```
favourites = astro, lifestyle, ocean, abstract, nature, art, animals, paintings, world, random
```
or
```
favourites = astro,lifestyle,ocean,       abstract,        nature,art,animals,paintings,world, random
```

- Adjust genre randomisation
```
randomise_genres = true
```

- Pick how you fill the screen

To fit images without cutting then out pill color fills the blank.
You can use the average color `avg_color` from Pexels.com or define your own.
```
use_average_color = true | false
fallback_fill_color = #000000
```

- Define the watch

```
[WATCH]
enabled = true
font_scale = 2
font_thickness = 2
offset_bottom_right_x = 200
offset_bottom_right_y = 200
offset_shadow = 3
max_random_offset_jump = 50
```

- Install the dependencies manually or use the pipenv

## Get api_key

- open https://www.pexels.com/
- register or login
- navigate to [Image & Video API](https://www.pexels.com/api/)
- get [Your API Key](https://www.pexels.com/api/new/)

## Working with pipenv

- Start pipenv
`pipenv shell`

## Running the main

- Run main with `./main.py` or `python main.py`
