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
        make_option('--unublished', action='store_true'),
        make_option('--ids'),
        make_option('--single-thread', action='store_true'),
        make_option('--from', help='from pk')
    )

    @transaction.autocommit
    def handle_noargs(self, **opts):
        map_ids = opts.get('ids')
        force = opts.get('force')

        pool = Pool(processes=4)

        maps = Map.objects.all()
        if not opts.get('unpublished'):
            maps = maps.filter(status=Map.STATUS_OK)
        maps = maps.order_by('pk')
        if map_ids:
            map_ids = map_ids.split(',')
            maps = maps.filter(pk__in=map_ids)
        if opts['from']:
            maps = maps.filter(pk__gte=opts['from'])

        print('going through {} maps'.format(maps.count()))

        counters = {'n_ok': 0, 'n_errs': 0, 'n_skip': 0}

        def log_stuff(force=False):
            n = sum(counters.values())
            if (n and not n % 10) or force:
                print('\rOK: {n_ok} skipped: {n_skip} errs: {n_errs}'.format(
                    **counters))

        results = []

        def drain_results():
            for mp, result in results:
                ok = result.get()
                log_stuff()
                if not ok:
                    print 'no thumbnail for map {}'.format(mp.pk)
                    counters['n_errs'] += 1
                    continue
                counters['n_ok'] += 1
            del results[:]

        for mp in maps.only('pk', 'thumbnail'):
            if STOP:
                break
            if not force and mp.thumbnail:
                counters['n_skip'] += 1
                continue

            if opts['single_thread']:
                generate_and_save(mp.pk)
                counters['n_ok'] += 1
            else:
                results.append((mp, pool.apply_async(generate_and_save, [mp.pk])))

            if len(results) >= BATCH_SIZE:
                drain_results()

        drain_results()

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
