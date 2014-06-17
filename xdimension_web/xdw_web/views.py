from __future__ import absolute_import

from django.views.generic.base import View
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site, get_current_site
from django.conf import settings

from xdimension_web.xdw_core.models import Map
from .opengraph import get_opengraph_context


class RobotsView(View):
    def get(self, request):
        # XXX disallow all crawlers
        return HttpResponse('User-agent: *\n'
                            'Disallow: /\n'
                            'Disallow: /admin\n\n'
                            'Sitemap: http://{site}{sitemap_url}\n'\
                                .format(site=Site.objects.get_current(),
                                        sitemap_url=reverse('sitemap')))


class AtlasView(View):
    def get(self, request, path='index.html'):
        return render(request, 'frontend/{}'.format(path))



class GraphDetailView(View):
    def get(self, request, pk, language=None):
        og_context = get_opengraph_context()
        map_ = get_object_or_404(Map, pk=pk, status=Map.STATUS_OK)
        site = get_current_site(request)
        
        def get_description(max_length, hashtags=False):
            desc, desc_len = [], 0
            for title in map_.node_titles:
                if hashtags and ' ' not in title:
                    title = u'#{}'.format(title)
                desc_len += len(title)
                if desc_len > 200 and desc:
                    break
                desc.append(title)
            return u' '.join(desc)

        # Facebook
        og_context.update({
            'og:title': map_.get_title(),
            'og:url': '{}://{}{}'.format(
                settings.SHARING_PROTO,
                site.domain,
                reverse('graph_detail', args=[settings.LANGUAGE_CODE, pk])),
            'og:image': map_.get_thumbnail_url(),
            'og:description': get_description(200),
        })

        # Twitter
        og_context.update({
            'twitter:card': 'summary_large_image',
            #'twitter:site': xxx
            'twitter:title': map_.get_title(),
            'twitter:description':  get_description(200, hashtags=True),
            #'twitter:creator': xxx
            'twitter:image:src': map_.get_thumbnail_url(),
            #'twitter:domain': XXX
        })
        return render(request, 'xdw_web/graph.html',
                      {'meta_items': og_context.items(),
                       'title': map_.get_title()})
