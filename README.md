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

`slide_duration` is in milliseconds

`max_slides_from_genre` will define how many images to play from one genre before moving to the next one
```
[BEHAVIOUR]
slide_duration = 15000
max_slides_from_genre = 50
```

- Adjust your preferred genres

Values are csv - space after coma is not required
```
[GENRES]
favourites = astro, lifestyle, ocean, abstract, nature, art, animals, paintings, world, random
```
or
```
[GENRES]
favourites = astro,lifestyle,ocean,       abstract,        nature,art,animals,paintings,world, random
```

- Adjust genre randomisation
```
randomise_genres = true
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
