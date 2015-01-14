# coding: utf8

from __future__ import absolute_import

import logging

from django.views.generic.base import View
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site, get_current_site
from django.conf import settings
from django.views.decorators.cache import cache_page

from xdimension_web.xdw_core.models import Map
from .opengraph import get_opengraph_context

logger = logging.getLogger(__name__)


class RobotsView(View):
    def get(self, request):
        return HttpResponse('User-agent: *\n'
                            'Allow: *\n'
                            'Disallow: /admin\n\n'
                            'Sitemap: http://{site}{sitemap_url}\n'\
                                .format(site=Site.objects.get_current(),
                                        sitemap_url=reverse('sitemap')))

ATLAS_DESCRIPTION = u'The Atlas of Human Knowledge is a collection of visual maps for learning and reference. Maps display semantic trees of correlations between topics, to quickly overview a knowledge area. Disclosure: LearnDiscovery mobile app is the tool adopted to create and collect knowledge maps within the Atlas.'

ATLAS_KEYWORDS = u'semantic, tree, trees, visual, learning, map, knowledge, mapping, connected, graph, graphs, education, discovery, ict4d, ict for development, share knowledge, learndiscovery, app'


class AtlasView(View):
    def get(self, request, path='index.html'):
        return render(request,
                      'frontend/{}'.format(path),
                      {'meta_items':
                           {'description': ATLAS_DESCRIPTION, 'keywords' : ATLAS_KEYWORDS},
                       # title is set by angular anyways
                       'title': 'Atlas of Human Knowledge - Visual maps, visualizing Wikipedia'}
        )



SHARING_FMT_LONG = (
    u'A visual map about {{topics}} and {{more_topics}} topics. '
    u'Make sense of semantic trees about: "{title}"! '
    u'This map visualizes a portion of the mind-map of the English Wikipedia - mapped at XDiscovery. '
    u'Correlations between topics are organized, so to effortlessly visualize and learn about a subject. '
    u'To map and save your own visual reference: LearnDiscovery mobile app (iOS). '
    #u'{url} | Made with #LearnDiscovery app >  Get the Human'
    #u'Knowledge in your hands > {app_url}'
)

SHARING_FMT_SHORT = (
    u'Learn in seconds: about {{topics}} and {{more_topics}} topics! '
    #u'{url} | Get your maps > {app_url}'
    u'Save your own visual references: LearnDiscovery mobile app (iOS)'
)

SHARING_FMT_TWITTER_CARD = (
    u'#VisualMap #SemanticTree {{topics}} + {{more_topics}} #wikipedia topics! '
    u'Save your own visual references: {app_url}'
)

GRAPH_DESCRIPTION_FMT = (
    u'A visual map about: {topics} '
    u'and other {more_topics} topics. Semantic trees for visual learning, created with LearnDiscovery mobile app. {more}'
)


GRAPH_KEYWORDS_FMT = (
    u'{keywords}, semantic tree, visual, learning, map, knowledge, mapping, connected, graph, graphs, education, discovery, learndiscovery, app '
  )


def topic_to_hashtag(topic):
    '''Turn a multi-word topic into an hastag.'''
    return u'#{}'.format(topic.title().replace(u' ', u''))


class GraphDetailView(View):

    def get(self, request, pk, language=None):
        og_context = get_opengraph_context()
        map_ = get_object_or_404(Map, pk=pk, status=Map.STATUS_OK)
        site = get_current_site(request)
        map_title = map_.get_title()
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
            return sep.join(desc), map_.node_count - len(desc)

        topics, more_topics = get_topics(hashtags=False)

        def get_keywords():
            desc = []
            sep = u', '
            for title in map_.node_titles[:10]:
                desc.append(title)
            return sep.join(desc)

        keywords = get_keywords()

        def get_long_description(**kwargs):
            desc_fmt = SHARING_FMT_LONG.format(
                title=map_title,
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
                                       more_topics=map_.node_count - 1)
                if len(desc) <= max_length:
                    return desc
                logger.warning('description too long for map {}'.format(map_.pk))
            logger.error('can\'t set description for map {}'.format(map_.pk))

        def get_twitter_card_description(max_length=200, **kwargs):
            desc_fmt = SHARING_FMT_TWITTER_CARD.format(
                url=map_url,
                app_url='http://tiny.cc/LearnDiscoveryApp'
            )
            for topic in map_.node_titles:
                topic_hashtag = topic_to_hashtag(topic)
                desc = desc_fmt.format(topics=topic_hashtag,
                                       more_topics=map_.node_count - 1)
                if len(desc) <= max_length:
                    return desc
                logger.warning('description too long for map {}'.format(map_.pk))
            logger.error('can\'t set description for map {}'.format(map_.pk))

        long_description = get_long_description()

        # Google crawler
        more = u'| {}'.format(map_.description) if map_.description else u''

        og_context.update({
            'description': GRAPH_DESCRIPTION_FMT.format(
                topics=topics,
                more_topics=more_topics,
                more=more),
            'keywords' : GRAPH_KEYWORDS_FMT.format(
                keywords=keywords
            ),
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
            'twitter:site': '@XDiscovery',
            'twitter:title': map_.get_title(),
            'twitter:description': get_twitter_card_description(),
            'twitter:creator': '@XDiscoveryWorld',
            'twitter:image:src': map_.get_thumbnail_url(),
            'twitter:domain': Site.objects.get_current()
        })
        return render(request, 'frontend/index.html',
                      {'meta': og_context,
                       'title': map_.get_title()})


@cache_page
def wip_page(request):
    '''Work in Progress.
    '''
    return render(request, 'xdw_web/wip.html')
