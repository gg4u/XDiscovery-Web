from __future__ import absolute_import

from djangocms_text_ckeditor.cms_plugins import TextPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _

from .models import BoxPluginModel, AbstractPluginModel


class CarouselPlugin(TextPlugin):
    name = _("Carousel Plugin")
    render_template = "xdw_web/cms_plugins/carousel.html"

plugin_pool.register_plugin(CarouselPlugin)


class BoxPlugin(CMSPluginBase):
    name = _("Box Plugin")
    render_template = "xdw_web/cms_plugins/box.html"
    model = BoxPluginModel

plugin_pool.register_plugin(BoxPlugin)


class AbstractPlugin(CMSPluginBase):
    name = _("Abstract Plugin")
    render_template = "xdw_web/cms_plugins/abstract.html"
    model = AbstractPluginModel

plugin_pool.register_plugin(AbstractPlugin)
