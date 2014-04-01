from django.shortcuts import render
from django.core.urlresolvers import reverse


class WIPMiddleware(object):

    def process_request(self, request):
        if (not request.user.is_authenticated() and
                not request.path.startswith(reverse('admin:index'))):
            return render(request, 'xdw_web/wip.html')
