import binascii
import json
import os
from typing import List, Tuple

from nazurin.models import Caption, Illust, Image
from nazurin.utils import Request
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

class DeviantArt(object):
    @network_retry
    async def get_deviation(self, deviation_id: int) -> dict:
        """Fetch a deviation."""
        api = "https://www.deviantart.com/_napi/da-user-profile/shared_api"\
            "/deviation/extended_fetch?type=art&deviationid=" + str(
            deviation_id)
        async with Request() as request:
            async with request.get(api) as response:
                if response.status == 404:
                    raise NazurinError('Deviation not found')
                response.raise_for_status()

                data = await response.json()
                if "error" in data.keys():
                    raise NazurinError(data['errorDescription'])

                deviation = data['deviation']
                del deviation['extended']['relatedContent']
                return deviation

    async def fetch(self, deviation_id: str) -> Illust:
        deviation = await self.get_deviation(deviation_id)
        imgs = self.get_images(deviation)
        caption = self.build_caption(deviation)
        return Illust(imgs, caption, deviation)

    def get_images(self, deviation: dict) -> List[Image]:
        """Get images from deviation."""
        filename, url, thumbnail = self.parse_url(deviation)
        original_file = deviation['extended']['originalFile']
        imgs = [
            Image(f"DeviantArt - {filename}", url, thumbnail,
                  original_file['filesize'], original_file['width'],
                  original_file['height'])
        ]
        return imgs

    def build_caption(self, deviation: dict) -> Caption:
        caption = Caption({
            'title': deviation['title'],
            'author': f"#{deviation['author']['username']}",
            'url': deviation['url']
        })
        if 'tags' in deviation['extended'].keys():
            caption['tags'] = ' '.join(
                ["#" + tag['name'] for tag in deviation['extended']['tags']])
        return caption

    def parse_url(self, deviation: dict) -> Tuple[str, str, str]:
        """
        Get filename, original file url & thumbnail url of deviation.
        """

        media = deviation['media']
        base_uri = media['baseUri']
        filename = f"{deviation['title']} - {deviation['deviationId']}"
        filename += os.path.splitext(base_uri)[1]

        tokens = media['token']
        types = dict()
        for type_ in media['types']:
            types[type_['t']] = type_

        path = '/f/' + base_uri.split('/f/')[1]
        url = base_uri + '?token=' + self.generate_token(path)

        token = tokens[0]
        if 'fullview' in types.keys():
            thumbnail = types['fullview']
            # Sometimes fullview has no subpath but there're two tokens,
            # in that case the base_uri should be used along with the second token
            # e.g. https://www.deviantart.com/exitmothership/art/Unfold-879580475
            if 'c' not in thumbnail.keys() and len(tokens) > 1:
                thumbnail['c'] = ''
                token = tokens[1]
        else:
            thumbnail = types['preview']
        thumbnail = base_uri + thumbnail['c'].replace('<prettyName>',
                                                      media['prettyName'])
        thumbnail = f"{thumbnail}?token={token}"

        return filename, url, thumbnail

    def generate_token(self, path: str) -> str:
        header = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0'  # {"typ":"JWT","alg":"none"}
        payload = {
            "sub": "urn:app:",
            "iss": "urn:app:",
            "obj": [[{
                "path": path
            }]],
            "aud": ["urn:service:file.download"]
        }
        payload = json.dumps(payload).encode()
        payload = binascii.b2a_base64(payload).rstrip(b"=\n").decode()
        return f"{header}.{payload}."
