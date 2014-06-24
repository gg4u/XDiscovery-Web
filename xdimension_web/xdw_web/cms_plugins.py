from __future__ import absolute_import
import logging

from cms.plugin_base import CMSPluginBase
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool
from cms.utils.plugins import get_plugins
from djangocms_text_ckeditor.widgets import TextEditorWidget
from djangocms_text_ckeditor.utils import plugin_tags_to_user_html
from django.forms.fields import CharField
from django.utils.translation import ugettext as _

from .models import (BoxPluginModel, AbstractPluginModel, AccordionPluginModel,
                     CarouselPluginModel)
from .admin import CarouselContentInline


logger = logging.getLogger(__name__)


class CarouselPlugin(CMSPluginBase):
    name = _("Carousel Plugin")
    render_template = "xdw_web/cms_plugins/carousel.html"
    model = CarouselPluginModel
    inlines = [CarouselContentInline]
    cache = False  # XXX caching breaks static_placeholder

    def render(self, context, instance, placeholder):
        context.update({'instance': instance, 'placeholder': placeholder})
        try:
            current_page = context['current_page']
        except KeyError:
            logger.error('can\'t find current page...')
            return context
        items = []
        current_page = context['current_page']
        active_item_idx = 0
        for i, c in enumerate(instance.carouselcontent_set.all()):
            if (c.page is not None and
                (c.page == current_page or
                 c.page.publisher_public_id == current_page.pk)):
                active_item_idx = i
            items.append(c)
        logger.debug('selected carousel item {}'.format(active_item_idx))
        context.update({
            'carouselcontent_items': items,
            'carouselcontent_active_item_idx': active_item_idx
        })
        return context


plugin_pool.register_plugin(CarouselPlugin)


class TextMixin(object):
    change_form_template = "cms/plugins/text_plugin_change_form.html"

    def get_form(self, request, obj=None, **kwargs):
        # Augment the form with the plugin info
        plugins = plugin_pool.get_text_enabled_plugins(
            self.placeholder,
            self.page
        )
        pk = self.cms_plugin_instance.pk
        widget = TextEditorWidget(
            installed_plugins=plugins, pk=pk,
            placeholder=self.placeholder,
            plugin_language=self.cms_plugin_instance.language
        )

        form_class = super(TextMixin, self).get_form(
            request, obj=obj, **kwargs)
        form_class.declared_fields["body"] = CharField(
            widget=widget, required=False
        )

        kwargs['form'] = form_class  # override standard form
        return super(TextMixin, self).get_form(
            request, obj=obj, **kwargs)

    def render(self, context, instance, placeholder):
        context = super(TextMixin, self).render(context, instance,
                                                      placeholder)
        context['body'] = plugin_tags_to_user_html(
                instance.body,
                context,
                placeholder
        )
        return context


class BoxPlugin(TextMixin, CMSPluginBase):
    name = _("Box Plugin")
    render_template = "xdw_web/cms_plugins/box.html"
    model = BoxPluginModel
    allow_children = True

    def render(self, context, instance, placeholder):
        context = super(BoxPlugin, self).render(context, instance, placeholder)
        instance.body = context['body']
        more = instance.page_external
        if not more and instance.page is not None:
            more = instance.page.get_absolute_url()
        context.update({
            'more': more,
            'instance': instance,
            'placeholder': placeholder
        })
        return context

plugin_pool.register_plugin(BoxPlugin)


class AbstractPlugin(CMSPluginBase):
    name = _("Abstract Plugin")
    render_template = "xdw_web/cms_plugins/abstract.html"
    model = AbstractPluginModel

plugin_pool.register_plugin(AbstractPlugin)


class AccordionNavigationPlugin(CMSPluginBase):
    name = _("Accordion navigation Plugin")
    render_template = "xdw_web/cms_plugins/accordion_navigation.html"
    model = CMSPlugin

    def render(self, context, instance, placeholder):
        # Get all accordion plugins contained in the accordion placeholder
        # TODO: cache all this stuff
        page = instance.page
        try:
            target_placeholder = page.placeholders.filter(slot='accordion')[0]
        except IndexError:
            pass
        else:
            # XXX fallback language not implemented
            context['accordion_items'] = [
                p.get_plugin_instance()[0]
                for p in get_plugins(context['request'],
                                     target_placeholder,
                                     self.render_template)]
        return context

plugin_pool.register_plugin(AccordionNavigationPlugin)


class AccordionPlugin(TextMixin, CMSPluginBase):
    name = _("Accordion Plugin")
    render_template = "xdw_web/cms_plugins/accordion.html"
    model = AccordionPluginModel
    allow_children = True


plugin_pool.register_plugin(AccordionPlugin)
