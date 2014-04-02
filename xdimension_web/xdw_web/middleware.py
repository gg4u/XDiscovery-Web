from django.shortcuts import render
from django.core.urlresolvers import reverse


OK_URLS = ['/en/atlas', '/api', '/views', '/map', '/graph']


class WIPMiddleware(object):

    def process_request(self, request):
        if (not request.user.is_authenticated() and
                not request.path.startswith(reverse('admin:index')) and
                not [None for x in OK_URLS if request.path.startswith(x)] and
                not request.GET.get('angular') and
                not request.is_ajax()):
            return render(request, 'xdw_web/wip.html')
