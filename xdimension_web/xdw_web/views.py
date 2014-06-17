# coding: utf8

from __future__ import absolute_import

import logging

from django.views.generic.base import View
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site, get_current_site
from django.conf import settings

from xdimension_web.xdw_core.models import Map
from .opengraph import get_opengraph_context

logger = logging.getLogger(__name__)


class RobotsView(View):
    def get(self, request):
        # XXX disallow all crawlers
        return HttpResponse('User-agent: *\n'
                            'Allow: /en/graph\n'
                            'Allow: /en/atlas\n'
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
        map_url = '{}://{}{}'.format(
                settings.SHARING_PROTO,
                site.domain,
                reverse('graph_detail', args=[settings.LANGUAGE_CODE, pk]))
        desc_fmt_1 = (
            u'A map about: {{topics}} and other #{{more_topics}} topics! '
            u'{url} |'
            u'Get Human Knowledge in your hands > '
            u'#LearnDiscovery app {app_url}')
        # TODO: confirm app url
        desc_fmt = desc_fmt_1.format(url=map_url,
                                     app_url='http://bit.ly/1pcHMZ3'
        )

        def possible_descriptions(max_length, hashtags=True):
            desc = []
            sep = u' · '
            for title in map_.node_titles[:3]:
                if hashtags:
                    title = title.replace(' ', '')
                    title = u'#{}'.format(title)
                desc.append(title)
            yield desc_fmt.format(
                topics=sep.join(desc),
                more_topics=len(map_.node_titles) - len(desc)
            )
            yield sep.join(desc)
            yield desc[0]

        def get_description(max_length, **kwargs):
            for description in possible_descriptions(max_length, **kwargs):
                if len(description) <= max_length:
                    return description
                logger.warning('description too long for map {}'.format(map_.pk))
            logger.error('can\'t set description for map {}'.format(map_.pk))

        # Facebook
        og_context.update({
            'og:title': map_.get_title(),
            'og:url': map_url,
            'og:image': map_.get_thumbnail_url(),
            'og:description': get_description(500),
        })

        # Twitter
        og_context.update({
            'twitter:card': 'summary_large_image',
            #'twitter:site': xxx
            'twitter:title': map_.get_title(),
            'twitter:description': get_description(200),
            #'twitter:creator': xxx
            'twitter:image:src': map_.get_thumbnail_url(),
            #'twitter:domain': XXX
        })
        return render(request, 'xdw_web/graph.html',
                      {'meta_items': og_context.items(),
                       'title': map_.get_title()})
