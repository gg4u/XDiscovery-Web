from __future__ import division

import os
from StringIO import StringIO
import itertools

import requests
from PIL import Image, ImageFont, ImageDraw
from django.core.files import File

# Tiles in a thumbnail
MAX_TILES = 5

IMAGE_WIDTH = 300

FETCH_BATCH_SIZE = 50

DEBUG = False


def left_column_n_tiles(images):
    '''How many tiles in the left column?

    Params:
        tiles as Image instances.

    Returns:
        an integer representing how many tiles to put in the first column.
    '''
    return 1 if len(images) == 3 else 2


def fetch_page_images(page_ids):
    '''Get image urls from wikipedia. '''
    while True:
        ids = [id_ for id_ in itertools.islice(page_ids, 0, FETCH_BATCH_SIZE)]
        if not ids:
            break
        resp = requests.get(
            'http://en.wikipedia.org/w/api.php',
            params={'pageids': '|'.join(str(i) for i in ids),
                    'action': 'query',
                    'format': 'json',
                    'prop': 'pageimages|extracts',
                    'pilimit': len(ids),
                    'pithumbsize': 400,
                    'exlimit': len(ids),
                    'exintro': 1,
                    'exsentences': 1,
                    'redirects': ''}
        )
        resp.raise_for_status()
        for _, page_info in resp.json()['query']['pages'].items():
            try:
                yield page_info['thumbnail']['source']
            except KeyError:
                pass
            

def download_images(urls):
    '''Download images and turn them into an Image.'''
    for url in urls:
        resp = requests.get(url)
        resp.raise_for_status()
        yield Image.open(StringIO(resp.content))


TEXT_MARGIN = 10
FONT_FNAME = os.path.join(os.path.dirname(__file__), 'fonts', 'sans.ttf')

def make_text_images(map_instance):
    titles = ['One', 'Two oo']
    font = ImageFont.truetype(FONT_FNAME, 100)
    for title in titles:
        size = [x + TEXT_MARGIN for x in font.getsize(title)]
        image = Image.new('RGB', size, '#1c1e1f')
        draw = ImageDraw.Draw(image)
        draw.text((TEXT_MARGIN/2, TEXT_MARGIN*-2), title, font=font)
        yield image


def make_thumbnail(images, map_instance):
    '''Build the thumbnail tiling the images.

    Arranges the tiles in two columns.

    Params:
        an iterable of Image tiles.

    Returns:
        an in-memory Image with the thumbnail or None if not enough tiles
    '''
    L = IMAGE_WIDTH
    images = itertools.chain(images, make_text_images(map_instance))
    images = [image for image in itertools.islice(images, MAX_TILES)]
    if not images:
        return
    n1 = left_column_n_tiles(images)
    if DEBUG:
        print('original size: {}'.format([image.size for image in images]))
    # Calculate first scaling factor
    scaling1 = [L / image.size[0] for image in images]
    # Calculate H1 and H2
    H1 = sum(image.size[1] * s for image, s in itertools.islice(zip(images, scaling1), n1))
    H2 = sum(image.size[1] * s for image, s in itertools.islice(zip(images, scaling1), n1, None))
    alpha = H2 / (H1 + H2) if H2 else 1

    # Calculate tiles dimensions
    L1 = int(round(alpha * L))
    L2 = L - L1
    dimensions1 = [(L1, int(round(image.size[1] * alpha * s1)))
                   for image, s1 in zip(images, scaling1)[:n1]]
    H = sum(dim[1] for dim in dimensions1)
    dimensions2 = [(L2, int(round(image.size[1] * (1 - alpha) * s1)))
                   for image, s1 in zip(images, scaling1)[n1:]]
    if dimensions2:
        # fix height of right bottom tile
        dimensions2[-1] = (dimensions2[-1][0],
                           H - sum(dim[1] for dim in dimensions2[:-1]))
    dimensions = itertools.chain(dimensions1, dimensions2)
    if DEBUG:
        print('tile size: {}'.format([dimensions1 + dimensions2]))
    del image

    # Combine all tiles in a single image
    thumbnail = Image.new('RGBA', (L, H))
    if DEBUG:
        print('thumbnail size: {}'.format(thumbnail.size))
    x, y = 0, 0
    i = 0
    for dim, image in itertools.izip(dimensions, images):
        image = image.resize(dim, resample=Image.ANTIALIAS)
        thumbnail.paste(image, (x, y))
        i += 1
        if i == n1:
            x += dim[0]
            y = 0
        else:
            y += dim[1]
    return thumbnail


def get_map_page_ids(map_instance):
    '''Wikipedia page ids in a map.

    Returns:
        a generator yielding page ids as strings.
    '''
    so_far = set()
    data = map_instance.map_data['map']
    # Tapped
    ids = data.get('tappedNodes', [])
    for id_ in ids:
        if id_ not in so_far:
            id_ = str(id_)
            yield id_
            so_far.add(id_)
    # Pagerank
    for node in data.get('pagerank', []):
        id_ = str(node['id'])
        if id_ not in so_far:
            so_far.add(id_)
            yield id_
    # All nodes
    for node in data.get('graph', []):
        for id_ in (node['source'], node['target']):
            id_ = str(id_)
            if id_ not in so_far:
                so_far.add(id_)
                yield id_


def generate_map_thumbnail(map_instance):
    '''Build a thumbnail for a map.

    Params:
        a map instance

    Returns:
        an in-memory Image.
    '''
    ids = get_map_page_ids(map_instance)
    urls = fetch_page_images(ids)
    images = download_images(urls)
    # XXX For testing
    # images = [Image.open('{}.jpg'.format(i)) for i in range(5)]
    thumbnail = make_thumbnail(images, map_instance)
    return thumbnail


def save_map_thumbnail(map_instance, thumb, commit=True):
    '''Persist the thumbnail in a map instance.

    Params:
        - a map instance,
        - the thumbnail
    '''
    thumb_file = File(StringIO())
    thumb.save(thumb_file, 'JPEG')
    map_instance.thumbnail.save('{}.jpg'.format(map_instance.pk), thumb_file)
    map_instance.thumbnail_status = map_instance.THUMBNAIL_STATUS_OK
    if commit:
        map_instance.save(update_fields=['thumbnail', 'thumbnail_status'])
