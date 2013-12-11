from __future__ import absolute_import

from cms.plugin_base import CMSPluginBase
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool
from cms.plugins.utils import get_plugins
from djangocms_text_ckeditor.widgets import TextEditorWidget
from django.forms.fields import CharField
from django.utils.translation import ugettext as _

from .models import (BoxPluginModel, AbstractPluginModel, AccordionPluginModel,
                     CarouselPluginModel)
from .admin import CarouselContentInline
from .admin_forms import BoxForm


class CarouselPlugin(CMSPluginBase):
    name = _("Carousel Plugin")
    render_template = "xdw_web/cms_plugins/carousel.html"
    model = CarouselPluginModel
    inlines = [CarouselContentInline]

    def render(self, context, instance, placeholder):
        context.update({
            'carouselcontent_items': [c for c in instance.carouselcontent_set.all()],
            'instance': instance,
            'placeholder': placeholder
        })
        return context


plugin_pool.register_plugin(CarouselPlugin)


class BoxPlugin(CMSPluginBase):
    name = _("Box Plugin")
    render_template = "xdw_web/cms_plugins/box.html"
    model = BoxPluginModel
    form = BoxForm

    def render(self, context, instance, placeholder):
        context.update({
            'more': instance.page_external or instance.page,
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
                                     target_placeholder)]
        return context

plugin_pool.register_plugin(AccordionNavigationPlugin)


class AccordionPlugin(CMSPluginBase):
    name = _("Accordion Plugin")
    render_template = "xdw_web/cms_plugins/accordion.html"
    model = AccordionPluginModel
    allow_children = True

    def get_form(self, request, obj=None, **kwargs):
        # Augment the form with the plugin info
        plugins = plugin_pool.get_text_enabled_plugins(
            self.placeholder,
            self.page
        )
        pk = self.cms_plugin_instance.pk
        widget = TextEditorWidget(installed_plugins=plugins, pk=pk)

        form_class = super(AccordionPlugin, self).get_form(
            request, obj=obj, **kwargs)
        form_class.declared_fields["body"] = CharField(
            widget=widget, required=False
        )

        kwargs['form'] = form_class  # override standard form
        return super(AccordionPlugin, self).get_form(
            request, obj=obj, **kwargs)


plugin_pool.register_plugin(AccordionPlugin)
