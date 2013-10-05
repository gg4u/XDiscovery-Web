from django.views.generic.base import View
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site


class RobotsView(View):
    def get(self, request):
        return HttpResponse('User-agent: *\n'
                            'Allow: *\n'
                            'Disallow: /admin\n\n'
                            'Sitemap: http://{site}{sitemap_url}\n'\
                                .format(site=Site.objects.get_current(),
                                        sitemap_url=reverse('sitemap')))
