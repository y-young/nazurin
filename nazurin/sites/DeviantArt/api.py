import binascii
import json
import os
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from nazurin.models import Caption, Illust, Image
from nazurin.models.file import File
from nazurin.utils import Request, logger
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError

class DeviantArt:
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
        file = await self.get_download(deviation)
        return Illust(imgs, caption, deviation, [file] if file else [])

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

    async def get_download(self, deviation: dict) -> Optional[File]:
        if not deviation['isDownloadable']:
            return None
        download = deviation['extended']['download']
        original_file = deviation['extended']['originalFile']

        if download['width'] and \
            download['filesize'] == original_file['filesize'] and \
            download['width'] == original_file['width'] and \
            download['height'] == original_file['height']:
            logger.info(
                "No need to download since it's the same as the original image"
            )
            return None

        author_uuid = deviation['author']['useridUuid']
        url = urlparse(deviation['media']['baseUri'])
        filename = os.path.basename(download['url']).split('?')[0]
        url = url._replace(netloc=url.netloc.replace('images-wixmp-',
                                                     'wixmp-'),
                           path=f"/f/{author_uuid}/{filename}")
        pretty_name = deviation['media']['prettyName'] + os.path.splitext(
            filename)[1]
        token = self.generate_token(url.path)
        return File(pretty_name, f"{url.geturl()}?token={token}")

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
        tokens = media['token'] if 'token' in media.keys() else []
        types = dict()
        for type_ in media['types']:
            types[type_['t']] = type_

        filename = f"{deviation['title']} - {deviation['deviationId']}"
        filename += os.path.splitext(base_uri)[1]

        path = urlparse(base_uri).path

        token = tokens[0] if len(tokens) > 0 else ''
        if path.startswith('/f/'):
            url = f"{base_uri}?token={self.generate_token(path)}"
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
            thumbnail = base_uri + thumbnail['c'].replace(
                '<prettyName>', media['prettyName'])
            thumbnail = f"{thumbnail}?token={token}"
        elif base_uri.endswith('.gif'):  # TODO: Send GIFs properly
            thumbnail = url = f"{types['gif']['b']}?token={token}"
        else:
            thumbnail = url = base_uri

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
