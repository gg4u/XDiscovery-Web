'''
Restore status of all Topic and MapTopic models.
'''
from optparse import make_option

from django.core.management.base import NoArgsCommand
from django.db import transaction

from xdimension_web.xdw_core.models import Map
from xdimension_web.xdw_core.thumbs import (generate_map_thumbnail,
                                            save_map_thumbnail)


class Command(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
        make_option('--force', action='store_true'),
        make_option('--ids')
    )

    @transaction.autocommit
    def handle_noargs(self, **opts):
        map_ids = opts.get('id')
        force = opts.get('force')

        maps = Map.objects.all()
        if map_ids:
            map_ids = map_ids.split(',')
            maps = maps.filter(pk__in=map_ids)

        print('going through {} maps'.format(maps.count()))

        n_skip, n_errs, n_ok = 0, 0, 0

        def log_stuff(force=False):
            n = n_skip + n_errs + n_ok
            if (n or force) and not n % 10:
                print('\rOK: {} skipped: {} errs: {}'.format(
                    n_ok, n_skip, n_errs))

        for mp in maps:
            log_stuff()
            if not force and mp.thumbnail is not None:
                n_skip += 1
                continue
            thumb = generate_map_thumbnail(mp)
            if thumb is None:
                print 'no thumbnail for map {}'.format(mp.pk)
                n_errs += 1
                continue
            save_map_thumbnail(mp, thumb)
            n_ok += 1
        log_stuff(force=True)
