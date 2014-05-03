import signal
import time
import logging

from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.db import transaction
import zmq

from xdimension_web.xdw_core.models import Map
from xdimension_web.xdw_core.thumbs import (generate_map_thumbnail,
                                            save_map_thumbnail)

POLL_TIMEOUT = 10000

_EXIT = False

logger = logging.getLogger(__name__)

def handle_sigterm(signum, frame):
    global _EXIT
    _EXIT = True


class Command(NoArgsCommand):


    @transaction.commit_manually
    def handle_noargs(self, **opts):
        signal.signal(signal.SIGTERM, handle_sigterm)

        ctx = zmq.Context.instance()
        sock = ctx.socket(zmq.SUB)
        sock.setsockopt(zmq.SUBSCRIBE, '')
        sock.bind('tcp://127.0.0.1:{}'.format(settings.ZMQ_WORKER_PORT))

        while True:
            # do the work
            for mp in Map.objects.filter(thumbnail_status=Map.THUMBNAIL_STATUS_DIRTY).only('pk', 'thumbnail', 'status', 'thumbnail_status'):
                try:
                    logger.info('generating thumbnail for map {}...'.format(mp.pk))
                    start = time.time()
                    thumb = generate_map_thumbnail(mp)
                    save_map_thumbnail(mp, thumb, commit=False)
                    update_fields = ['thumbnail', 'thumbnail_status']
                    mp.thumbnail_status = Map.THUMBNAIL_STATUS_OK
                    if mp.status == Map.STATUS_PUBLISHING:
                        mp.status = Map.STATUS_OK
                        update_fields.append(['status'])
                    logger.info('done generating thumbnail in {} s'.format(time.time() - start))
                    mp.save(update_fields=update_fields)
                    transaction.commit()
                except:
                    transaction.rollback()
                    raise
            if sock.poll(POLL_TIMEOUT):
                try:
                    mesg = sock.recv(flags=zmq.NOBLOCK)
                    logger.info(u'received "{}"'.format(mesg))
                except zmq.ZMQError:
                    pass
        sock.close()
        logger.info('exiting')
