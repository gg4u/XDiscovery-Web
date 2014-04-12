from __future__ import division

import requests
from PIL import Image
from StringIO import StringIO
import itertools
import math
from django.core.files import File

# Images in a thumbnail
MAX_IMAGES = 5

IMAGE_WIDTH = 300

DEBUG = False


def fetch_page_images(page_ids):
    ids = page_ids[:MAX_IMAGES]
    if len(ids) < MAX_IMAGES:
        return
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
    for _, page_info in resp.json()['query']['pages'].items():
        try:
            yield page_info['thumbnail']['source']
        except KeyError:
            pass


def download_images(urls):
    for url in urls:
        resp = requests.get(url)
        resp.raise_for_status()
        yield Image.open(StringIO(resp.content))


def make_thumbnail(images):
    n1 = 2
    n2 = 3
    n = n1 + n2
    L = IMAGE_WIDTH
    images = [image for image in itertools.islice(images, n1 + n2)]
    if len(images) < n:
        return
    if DEBUG:
        print('original size: {}'.format([image.size for image in images]))
    # Calculate first scaling factor
    scaling1 = [L / image.size[0] for image in images]
    # Calculate H1 and H2
    H1 = sum(image.size[1] * s for image, s in itertools.islice(zip(images, scaling1), n1))
    H2 = sum(image.size[1] * s for image, s in itertools.islice(zip(images, scaling1), n1, None))
    alpha = H2 / (H1 + H2)

    # Calculate tiles dimensions
    L1 = int(round(alpha * L))
    L2 = L - L1
    dimensions1 = [(L1, int(round(image.size[1] * alpha * s1)))
                   for image, s1 in zip(images, scaling1)[:n1]]
    H = sum(dim[1] for dim in dimensions1)
    dimensions2 = [(L2, int(round(image.size[1] * (1 - alpha) * s1)))
                   for image, s1 in zip(images, scaling1)[n1:]]
    # fix height of right bottom tile
    dimensions2[-1] = (dimensions1[-1][0],
                       H - sum(dim[1] for dim in dimensions2[:-1]))
    dimensions = itertools.chain(dimensions1, dimensions2)
    if DEBUG:
        print('tile size: {}'.format([dimensions1 + dimensions2]))
    del image

    # Combine all tiles in a single image
    thumbnail = Image.new(images[0].mode, (L, H))
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


def generate_map_thumbnail(map_instance):
    data = map_instance.map_data['map']
    ids = data.get('tappedNodes', [])
    urls = fetch_page_images(ids)
    images = download_images(urls)
    # XXX For testing
    # images = [Image.open('{}.jpg'.format(i)) for i in range(5)]
    thumbnail = make_thumbnail(images)
    return thumbnail


def save_map_thumbnail(map_instance, thumb, commit=True):
    thumb_file = File(StringIO())
    thumb.save(thumb_file, 'JPEG')
    map_instance.thumbnail.save('{}.jpg'.format(map_instance.pk), thumb_file)
    if commit:
        map_instance.save(update_fields=['thumbnail'])
