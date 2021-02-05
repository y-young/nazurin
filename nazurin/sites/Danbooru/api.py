import re
from os import path
from typing import List, Optional, Tuple

from pybooru import Danbooru as danbooru
from pybooru import PybooruHTTPError

from nazurin.models import Caption, Image
from nazurin.utils import downloadImages
from nazurin.utils.exceptions import NazurinError

class Danbooru(object):
    def __init__(self, site='danbooru'):
        """Set Danbooru site."""
        self.site = site
        self.api = danbooru(site)

    def getPost(self,
                post_id: Optional[int] = None,
                md5: Optional[str] = None):
        """Fetch an post."""
        try:
            if post_id:
                post = self.api.post_show(post_id)
            else:
                post = self.api.post_list(md5=md5)
        except PybooruHTTPError as err:
            if 'Not Found' in err._msg:
                raise NazurinError('Post not found') from None
        if 'file_url' not in post.keys():
            raise NazurinError(
                'You may need a gold account to view this post\nSource: ' +
                post['source'])
        return post

    def view(self, post_id: int) -> Tuple[List[Image], Caption]:
        post = self.getPost(post_id)
        imgs, caption = self.parsePost(post)
        return imgs, caption

    async def download(self,
                       post_id: Optional[int] = None,
                       post=None) -> List[Image]:
        if post:
            imgs, _ = self.parsePost(post)
        else:
            imgs, _ = self.view(post_id)
        await downloadImages(imgs)
        return imgs

    def parsePost(self, post) -> Tuple[List[Image], Caption]:
        """Get images and build caption."""
        # Get images
        url = post['file_url']
        artists = post['tag_string_artist']
        title, filename = self._getNames(post)
        imgs = list()
        imgs.append(Image(filename, url))

        # Build media caption
        tags = post['tag_string'].split(' ')
        tag_string = str()
        for character in tags:
            tag_string += '#' + character + ' '
        caption = Caption({
            'title': title,
            'artists': artists,
            'url': 'https://' + self.site + '.donmai.us/posts/' +
            str(post['id']),
            'tags': tag_string,
            'parent_id': post['parent_id'],
            'pixiv_id': post['pixiv_id'],
            'has_children': post['has_children']
        })
        return imgs, caption

    def _getNames(self, post) -> Tuple[str, str]:
        """Build title and filename."""
        characters = self._formatCharacters(post['tag_string_character'])
        copyrights = self._formatCopyrights(post['tag_string_copyright'])
        artists = self._formatArtists(post['tag_string_artist'])
        extension = path.splitext(post['file_url'])[1]
        filename = str()

        if characters:
            filename += characters + ' '
        if copyrights:
            if characters:
                copyrights = '(' + copyrights + ')'
            filename += copyrights + ' '
        title = filename
        if artists:
            filename += 'drawn by ' + artists
        filename = 'danbooru ' + str(post['id']) + ' ' + filename + extension
        return title, filename

    def _formatCharacters(self, characters: str) -> str:
        if not characters:
            return ''
        characters = characters.split(' ')
        characters = list(map(self._normalize, characters))
        size = len(characters)
        if size <= 5:
            result = self._sentence(characters)
        else:
            characters = characters[:5]
            result = self._sentence(characters) + ' and ' + str(size -
                                                                1) + ' more'
        return result

    def _formatCopyrights(self, copyrights: str) -> str:
        if not copyrights:
            return ''
        copyrights = copyrights.split(' ')
        copyrights = list(map(self._normalize, copyrights))
        size = len(copyrights)
        if size == 1:
            result = copyrights[0]
        else:
            result = copyrights[0] + ' and ' + str(size - 1) + ' more'
        return result

    def _formatArtists(self, artists: str) -> str:
        if not artists:
            return ''
        return self._normalize(self._sentence(artists.split(' ')))

    def _sentence(self, names: List[str]) -> str:
        if len(names) == 1:
            return names[0]
        else:
            sentence = ' '.join(names[:-1])
            sentence += ' and ' + names[-1]
            return sentence

    def _normalize(self, name: str) -> str:
        name = re.sub(r'_\(.*\)', '', name)  # replace _(...)
        name = name.replace('_', ' ')
        name = re.sub(r'[\\\/]', ' ', name)  # replace / and \
        return name
