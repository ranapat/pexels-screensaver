import shutil
import urllib.parse

import requests


class RestApi:
    def __init__(self, config):
        self._config = config

    def _escape(self, value: str) -> str:
        return urllib.parse.quote(value)

    def _normalize_url(self, path: str, parameters: dict[str, str], quote_parameters: bool = True) -> str:
        _parameters = parameters

        __parameters = {k: self._escape(v) if quote_parameters else v for k, v in _parameters.items()}
        __parameters_string = '&'.join([f'{key}={value}' for key, value in __parameters.items()])

        return f'{path}?{__parameters_string}'

    def _normalize_headers(self, headers: dict[str, str]) -> dict[str, str]:
        headers[self._config.rest_header_authorization_key] = self._config.account_api_key
        return headers

    def get_json(self, path: str, parameters: dict[str, str] = {}, headers: dict[str, str] = {}):
        try:
            response = requests.get(
                url=self._normalize_url(path, parameters),
                headers=self._normalize_headers(headers),
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

    def persist(self, remote_url: str, local_path: str):
        print(f'### [ Saving ] {remote_url} to {local_path}')

        r = requests.get(remote_url, headers=self._normalize_headers({}), stream=True)
        with open(local_path, "wb") as out_file:
            shutil.copyfileobj(r.raw, out_file)