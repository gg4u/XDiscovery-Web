'''
Restore status of all Topic and MapTopic models.
'''
from optparse import make_option
from multiprocessing import Pool
import signal

from django.core.management.base import NoArgsCommand
from django.db import transaction

from xdimension_web.xdw_core.models import Map
from xdimension_web.xdw_core.thumbs import (generate_map_thumbnail,
                                            save_map_thumbnail)


BATCH_SIZE = 20  # For parallel processing

STOP = False


def stop_the_world(signal, frame):
    global STOP
    STOP = True

signal.signal(signal.SIGINT, stop_the_world)


class Command(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
        make_option('--force', action='store_true'),
        make_option('--ids')
    )

    @transaction.autocommit
    def handle_noargs(self, **opts):
        map_ids = opts.get('ids')
        force = opts.get('force')

        pool = Pool(processes=4)

        maps = Map.objects.all()
        if map_ids:
            map_ids = map_ids.split(',')
            maps = maps.filter(pk__in=map_ids)

        print('going through {} maps'.format(maps.count()))

        n_skip, n_errs, n_ok = 0, 0, 0

        def log_stuff(force=False):
            n = n_skip + n_errs + n_ok
            if (n and not n % 10) or force:
                print('\rOK: {} skipped: {} errs: {}'.format(
                    n_ok, n_skip, n_errs))

        results = []


        for mp in maps.only('pk', 'thumbnail'):
            if not force and mp.thumbnail:
                n_skip += 1
                continue
            results.append((mp, pool.apply_async(generate_and_save, [mp.pk])))
            if STOP or len(results) >= BATCH_SIZE:
                if STOP:
                    print 'waiting for all processes to terminate...'
                for mp, result in results:
                    ok = result.get()
                    log_stuff()
                    if not ok:
                        print 'no thumbnail for map {}'.format(mp.pk)
                        n_errs += 1
                        continue
                    n_ok += 1
                results = []

            if STOP:
                break
        pool.close()
        pool.join()
        log_stuff(force=True)


def generate_and_save(map_id):

    # A python nonsense: child processes inherit fds...
    from django.db import connection
    connection.close()

    mp = Map.objects.get(pk=map_id)
    thumb = generate_map_thumbnail(mp)
    if thumb is None:
        return False
    save_map_thumbnail(mp, thumb)
    return True
