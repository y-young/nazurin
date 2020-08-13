import os
import re
from utils import NazurinError, downloadImages, sanitizeFilename
from pybooru import Danbooru as danbooru, PybooruHTTPError

class Danbooru(object):
    api = danbooru('danbooru')
    def view(self, post_id):
        try:
            post = self.api.post_show(post_id)
        except PybooruHTTPError as err:
            if 'Not Found' in err._msg:
                raise NazurinError('Post not found')
        if 'file_url' not in post.keys():
            raise NazurinError('You may need a gold account to view this post\nSource: ' + post['source'])

        url = post['file_url']
        artists = post['tag_string_artist']
        tags = post['tag_string'].split(' ')
        title, filename = self._getNames(post)
        imgs = list()
        imgs.append({'url': url, 'name': filename})

        tag_string = str()
        for character in tags:
            tag_string += '#' + character + ' '
        details = dict()
        if title:
            details['title'] = title
        if artists:
            details['artists'] = artists
        details.update({'url': 'https://danbooru.donmai.us/posts/' + str(post_id), 'tags': tag_string})
        if post['parent_id']:
            details['parent_id'] = post['parent_id']
        if post['pixiv_id']:
            details['pixiv_id'] = post['pixiv_id']
        if post['has_children']:
            details['has_children'] = True
        return imgs, details

    def download(self, post_id):
        imgs, _ = self.view(post_id)
        downloadImages(imgs)
        return imgs

    def _getNames(self, post):
        characters = post['tag_string_character']
        copyrights = post['tag_string_copyright']
        artists = post['tag_string_artist']
        filename = str()
        if characters:
            filename += self._formatCharacters(characters) + ' '
        if copyrights:
            copyrights = self._formatCopyrights(copyrights)
            if characters:
                filename += '(' + copyrights + ')'
            else:
                filename += copyrights
        title = filename
        if artists:
            filename += ' drawn by ' + self._normalize(self._sentence(artists.split(' ')))
        if filename: # characters or copyrights present
            filename += ' - '
        filename += os.path.basename(post['file_url'])
        return title, sanitizeFilename(filename)

    def _formatCharacters(self, characters):
        characters = characters.split(' ')
        characters = list(map(self._normalize, characters))
        size = len(characters)
        if size <= 5:
            result = self._sentence(characters)
        else:
            characters = characters[:5]
            result = self._sentence(characters) + ' and ' + str(size - 1) + ' more'
        return result

    def _formatCopyrights(self, copyrights):
        copyrights = copyrights.split(' ')
        copyrights = list(map(self._normalize, copyrights))
        size = len(copyrights)
        if size == 1:
            result = copyrights[0]
        else:
            result = copyrights[0] + ' and ' + str(size - 1) + ' more'
        return result

    def _sentence(self, names):
        if len(names) == 1:
            return names[0]
        else:
            sentence = ' '.join(names[:-1])
            sentence += ' and ' + names[-1]
            return sentence

    def _normalize(self, name):
        name = re.sub('_\(.*\)', '', name) # replace _(...)
        name = name.replace('_', ' ')
        name = re.sub('[\\\/]', ' ', name) # replace / and \
        return name