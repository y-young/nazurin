import os
import re
import sys
import glob
import random
import logging
from time import time, sleep

sys.path.append('../../')
from database import Database
from sites import SiteManager
from sites.Moebooru.config import COLLECTIONS as MOEBOORU_COLLECTIONS

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('helper')
sites = SiteManager()

success = file_cnt = artworks = 0
no_match = list()
directory = ''
error = list()
processed = {}
sites.load()
SITES = ['pixiv', 'danbooru', 'yandere', 'konachan', 'lolibooru', 'zerochan', 'twitter', 'bilibili']

def scan():
    patterns = {
        'pixiv': r'^(\d+)_(?:p\d|ugoira)',
        'bilibili': r'^(\d+)_\d',
        'twitter': r'^twitter - (\d+) -',
        'moebooru': r'(yande\.re|Konachan\.com|lolibooru)(?: -)? (\d+)',
        'danbooru': r' - ([a-f0-9]{32})\.',
        'danbooru_new': r'^danbooru (\d+)',
        'zerochan': r'^Zerochan (\d+)'
    }
    global file_cnt, no_match, directory
    files = glob.glob(directory + '*')
    for path in files:
        file_cnt = file_cnt + 1
        filename = path[len(directory):]
        flag = False

        for source, pattern in patterns.items():
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                flag = True
                break
        if not flag:
            no_match.append(filename)
            logger.warning(filename + ': ' + "No match")
            continue
        yield (filename, source, match)

def parseSource(source, match):
    collection = source
    origin_id = match.group(1)
    if source == 'moebooru':
        url = match.group(1)
        if url == 'lolibooru':
            url = 'lolibooru.moe'
        origin_id = int(match.group(2))
        collection = MOEBOORU_COLLECTIONS[url.lower()]
    elif source == 'danbooru':
        md5 = match.group(1)
        data = sites.api('danbooru').getPost(md5=md5)
        origin_id = data['id']
    return int(origin_id), collection

def process(filename, source, match, origin_id):
    api = sites.api(source)
    if source == 'pixiv':
        data = api.getArtwork(origin_id)
        sleep(random.random()+0.5) # Rate limit
    elif source == 'twitter':
        data = api.getTweet(origin_id)
    elif source == 'danbooru':
        data = api.getPost(origin_id)
        if not filename.startswith('danbooru'): # Rename old format to new
            _, newname = api._getNames(data)
            os.rename(directory + filename, directory + newname)
    elif source == 'moebooru':
        url = match.group(1)
        if url == 'lolibooru':
            url = 'lolibooru.moe'
        api = api.site(url)
        data, _ = api.getPost(origin_id)
    elif source == 'zerochan':
        data = api.getPost(origin_id)
    elif source == 'bilibili':
        data = api.getDynamic(origin_id)
    return data

def printResult():
    logger.info("Scanned Files: %d, Matched Artworks: %d, Processed: %d, No Match: %d, Error: %d", file_cnt, artworks, success, len(no_match), len(error))
    for key in processed.keys():
        logger.info("%s: processed %d", key, len(processed[key]))
    if no_match:
        logger.info("⚠️ No match:\n %s", no_match)
    if error:
        logger.info("❌ Error:\n %s", error)

def main():
    global artworks, success, directory, error, processed
    for source in SITES:
        processed[source] = list()
    directory = input('Directory path (ends with slash): ')
    print('Skip sites(enter site name in SITES, separated with comma):')
    print('SITES='+str(SITES))
    skipped = input()
    skipped = skipped.split(',')
    db = Database().driver()

    for filename, source, match in scan():
        origin_id, site = parseSource(source, match)
        if source == 'danbooru_new':
            source = site = 'danbooru'
        if site in skipped:
            continue

        if origin_id in processed[site]: # Pixiv multiple pages
            continue
        artworks = artworks + 1
        if db.collection(site).document(origin_id).exists():
            logger.info('⚪️ ' + filename + ': Already exists')
            processed[site].append(origin_id)
            continue

        try:
            data = process(filename, source, match, origin_id)
        except Exception as err:
            logger.error("❌ %s: (id: %s) %s", filename, origin_id, err)
            error.append((filename, origin_id, err))
            processed[site].append(origin_id)
            continue

        data['collected_at'] = time()
        db.collection(site).insert(origin_id, data)
        logger.info('✔️ ' + filename + ': ' + source + str(match.groups()))

        processed[site].append(origin_id)
        success = success + 1

    printResult()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        printResult()