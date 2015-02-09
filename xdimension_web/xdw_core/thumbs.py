from __future__ import division

import os
from StringIO import StringIO
import itertools
import logging

import requests
from PIL import Image, ImageFont, ImageDraw
from django.core.files import File

# Tiles in a thumbnail
MAX_TILES = 5

IMAGE_WIDTH = 300

FETCH_BATCH_SIZE = 50

logger = logging.getLogger(__name__)


def left_column_n_tiles(images):
    '''How many tiles in the left column?

    Params:
        tiles as Image instances.

    Returns:
        an integer representing how many tiles to put in the first column.
    '''
    return 1 if len(images) == 3 else 2


def fetch_page_images(page_ids):
    '''Get image urls from wikipedia.

    Returns:
       a generatorn yield the image URL or None if it can't be found.
    '''
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
        pages = resp.json()['query']['pages']
        for page_id in ids:
            try:
                yield pages[page_id]['thumbnail']['source']
            except KeyError:
                yield None
            

def download_images(urls):
    '''Download images and turn them into an Image.'''
    for url in urls:
        if url is None:
            yield None
        else:
            resp = requests.get(url)
            resp.raise_for_status()
            yield Image.open(StringIO(resp.content))


TEXT_MARGIN = 10
FONT_FNAME = os.path.join(os.path.dirname(__file__), 'fonts', 'sans.ttf')
#BG_COLOR = '#1c1e1f'
BG_COLOR = '#f7f7f7'
MAX_LINES = 3


def title_to_lines(title):
    return title.upper().split()


def get_rotations():
    return itertools.cycle((-10, 0, 10))


def make_text_image(text, rotation):
    '''Create an image representing text.

    Returns:
        an Image instance.
    '''
    font = ImageFont.truetype(FONT_FNAME, 100)
    # Tiles one per text line
    tiles = []
    width, height = 0, 0
    for line in itertools.islice(title_to_lines(text), MAX_LINES):
        size = [x + TEXT_MARGIN for x in font.getsize(line)]
        tile = Image.new('RGB', size, BG_COLOR)
        draw = ImageDraw.Draw(tile)
        draw.text((TEXT_MARGIN/2, TEXT_MARGIN*-2), line, font=font)
        tiles.append(tile)
        if tile.size[0] > width:
            width = tile.size[0]
        height += tile.size[1] + TEXT_MARGIN
    # Image containg all the lines (tiles)
    image = Image.new('RGB', (width, height), BG_COLOR)
    x, y = 0, 0
    for tile in tiles:
        image.paste(tile, ((image.size[0] - tile.size[0]) // 2, y))
        y += tile.size[1] + TEXT_MARGIN
    # Rotate the image, with a nice hack to set background
    image = image.convert('RGBA').rotate(rotation, resample=Image.BICUBIC,
                                         expand=1)
    bg = Image.new('RGBA', image.size, BG_COLOR)
    final = Image.composite(image, bg, image)
    final = final.convert('RGB')
    return final


def images_or_text(images, map_instance):
    '''Fill in missing images with text.

    Returns:
        a generator yielding images.
    '''
    rotations = get_rotations()
    for i, image in enumerate(images):
        if image is None:
            try:
                text = map_instance.node_titles[i]
            except IndexError:
                logger.warning('could not generate text image for topic {}'
                               .format(i))
                return
            else:
                rotation = next(rotations)
                yield make_text_image(text, rotation)
        else:
            yield image


def make_thumbnail(images):
    '''Build the thumbnail tiling the images.

    Arranges the tiles in two columns.

    Params:
        an iterable of Image tiles.

    Returns:
        an in-memory Image with the thumbnail or None if not enough tiles
    '''
    L = IMAGE_WIDTH
    images = [image for image in itertools.islice(images, MAX_TILES)]
    if not images:
        return
    n1 = left_column_n_tiles(images)
    if logger.isEnabledFor(logging.DEBUG):
        ('original size: {}'.format([image.size for image in images]))
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
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('tile size: {}'.format([dimensions1 + dimensions2]))
    del image

    # Combine all tiles in a single image
    thumbnail = Image.new('RGB', (L, H), BG_COLOR)
    logger.debug('thumbnail size: {}'.format(thumbnail.size))
    x, y = 0, 0
    i = 0
    for dim, image in itertools.izip(dimensions, images):
        if image.mode == 'RGBA':
            bg = Image.new('RGBA', image.size, BG_COLOR)
            image = Image.composite(image, bg, image)
            image = image.convert('RGB')
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
    # Pagerank
    for node in data.get('pagerank', []):
        id_ = str(node['id'])
        if id_ not in so_far:
            so_far.add(id_)
            yield id_
    # Tapped
    ids = data.get('tappedNodes', [])
    for id_ in ids:
        if id_ not in so_far:
            id_ = str(id_)
            yield id_
            so_far.add(id_)
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

    # Thumbnail should only contain images from the first 5 topics.
    images = images_or_text(images, map_instance)
    # Alternatively, thumbnail contains images from *all* topics
    #images = itertools.ifilter(lambda x: x is not None, images)

    thumbnail = make_thumbnail(images)
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
