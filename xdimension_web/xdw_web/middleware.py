import os.path
import logging

from django.core.urlresolvers import reverse
from django.conf import settings

# from .views import wip_page

logger = logging.getLogger(__name__)


class PartialResponseMiddleware(object):

    def process_template_response(self, request, response):
        if request.GET.get('angular'):
            template_name = getattr(response, 'template_name', None)
            if template_name:
                template_name = '{0}_angular{1}'.format(
                    *os.path.splitext(response.template_name)
                )
                response.template_name = template_name
            else:
                logger.warning('no template name found for {}'
                               .format(request.path))
        return response

OK_URLS = ['/en/atlas', '/api', '/views', '/map', '/en/graph', '/media',
           '/graph', '/atlas']

'''
# This class is for hiding front-page if due to errors
# uncomment in settings/common.py : ...WIPMiddleware 

class WIPMiddleware(object):

    def process_request(self, request):
        if (settings.HIDE_CONTENT and
                not request.user.is_authenticated() and
                not request.path.startswith(reverse('admin:index')) and
                not [None for x in OK_URLS if request.path.startswith(x)] and
                not request.GET.get('angular') and
                not request.is_ajax()):
            return wip_page(request)


'''