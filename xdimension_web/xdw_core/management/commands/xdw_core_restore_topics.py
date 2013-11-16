'''
Restore status of all Topic and MapTopic models.
'''

from django.core.management.base import NoArgsCommand
from django.db import transaction

from xdimension_web.xdw_core.models import Topic, MapTopic, Map
from xdimension_web.xdw_core.maps import save_map


class Command(NoArgsCommand):

    @transaction.commit_on_success
    def handle_noargs(self, **opts):
        Topic.objects.all().delete()
        MapTopic.objects.all().delete()
        for mp in Map.objects.all():
            save_map(mp)
