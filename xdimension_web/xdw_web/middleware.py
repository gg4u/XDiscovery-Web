from django.shortcuts import render
from django.core.urlresolvers import reverse


class PartialResponseMiddleware(object):

    def process_template_response(self, request, response):
        if request.GET.get('angular') or request.is_ajax():
            response.template_name = 'xdw_web/cms_templates/angular.html'
        return response


OK_URLS = ['/en/atlas', '/api', '/views', '/map', '/graph']


class WIPMiddleware(object):

    def process_request(self, request):
        if (not request.user.is_authenticated() and
                not request.path.startswith(reverse('admin:index')) and
                not [None for x in OK_URLS if request.path.startswith(x)] and
                not request.GET.get('angular') and
                not request.is_ajax()):
            return render(request, 'xdw_web/wip.html')
