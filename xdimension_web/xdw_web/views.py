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

ATLAS_DESCRIPTION = u'The Atlas of Human Knowledge is a collection of visual maps for learning and reference. Maps display knowledge correlations between topics, to quickly overview a knowledge area. Maps are obtained with LearnDiscovery mobile app, the portable discovery engine applied to factual knowledge.'

class AtlasView(View):
    def get(self, request, path='index.html'):
        return render(request,
                      'frontend/{}'.format(path),
                      {'meta_items': {'description': ATLAS_DESCRIPTION},
                       # title is set by angular anyways
                       'title': 'Atlas'}
        )

SHARING_FMT_LONG = (
    u'Learn in seconds: about {{topics}} and other {{more_topics}} topics! '
    u'{url} | Made with #LearnDiscovery app >  Get the Human'
    u'Knowledge in your hands > {app_url}'
)

SHARING_FMT_SHORT = (
    u'Learn in seconds: about {{topics}} and other {{more_topics}} topics! '
    u'{url} | Get your maps > {app_url}'
)

GRAPH_DESCRIPTION_FMT = (
    u'A knowledge map of correlations about: {topics} '
    u'and other {more_topics} topics | visual learning and discovery{more}'
)


class GraphDetailView(View):

    def get(self, request, pk, language=None):
        og_context = get_opengraph_context()
        map_ = get_object_or_404(Map, pk=pk, status=Map.STATUS_OK)
        site = get_current_site(request)
        map_url = '{}://{}{}'.format(
                settings.SHARING_PROTO,
                site.domain,
                reverse('graph_detail', args=[settings.LANGUAGE_CODE, pk]))

        def get_topics(hashtags=True):
            desc = []
            sep = u' · '
            for title in map_.node_titles[:3]:
                if hashtags:
                    title = title.replace(' ', '')
                    title = u'#{}'.format(title)
                desc.append(title)
            return sep.join(desc), len(map_.node_titles) - len(desc)

        topics, more_topics = get_topics()

        def get_long_description(**kwargs):
            desc_fmt = SHARING_FMT_LONG.format(
                url=map_url,
                app_url='http://tiny.cc/LearnDiscoveryApp'
            )
            return desc_fmt.format(topics=topics, more_topics=more_topics)

        def get_short_description(max_length=140, **kwargs):
            desc_fmt = SHARING_FMT_SHORT.format(
                url=map_url,
                app_url='http://tiny.cc/LearnDiscoveryApp'
            )
            for topic in map_.node_titles:
                desc = desc_fmt.format(topics=topic,
                                       more_topics=len(map_.node_titles) - 1)
                if len(desc) <= max_length:
                    return desc
                logger.warning('description too long for map {}'.format(map_.pk))
            logger.error('can\'t set description for map {}'.format(map_.pk))
    
        long_description = get_long_description()

        # Google crawler
        if map_.description:
            more = '| {description}'.format(map_.description)
        else:
            more = ''
        og_context.update({
            'description': GRAPH_DESCRIPTION_FMT.format(
                topics=topics,
                more_topics=more_topics,
                more=more),
            'title': map_.get_title(),  # Also set by angular
        })

        # Facebook
        og_context.update({
            'og:title': map_.get_title(),
            'og:url': map_url,
            'og:image': map_.get_thumbnail_url(),
            'og:description': long_description,
        })

        # Twitter
        og_context.update({
            'twitter:card': 'summary_large_image',
            #'twitter:site': xxx
            'twitter:title': map_.get_title(),
            'twitter:description': get_short_description(200),
            #'twitter:creator': xxx
            'twitter:image:src': map_.get_thumbnail_url(),
            #'twitter:domain': XXX
        })
        return render(request, 'frontend/index.html',
                      {'meta_items': og_context.items(),
                       'title': map_.get_title()})
