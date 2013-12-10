from cms.models.pluginmodel import CMSPlugin
from cms.models.pagemodel import Page

from djangocms_text_ckeditor.fields import HTMLField
from django.db import models
from django.core.exceptions import ValidationError


class BoxPluginModel(CMSPlugin):
    title = models.TextField(blank=True)
    body = HTMLField(blank=True)
    page = models.ForeignKey(Page, blank=True, null=True)
    page_external = models.CharField(max_length=1024, blank=True)
    style = models.CharField(max_length=10,
                             choices=(('normal', 'normal'),
                                      ('callout', 'callout')),
                             default='normal')

    def clean(self):
        if self.page and self.page_external:
            raise ValidationError('Page and External Page can\'t be both set')


class AbstractPluginModel(CMSPlugin):
    body = models.TextField(blank=True)


class AccordionPluginModel(CMSPlugin):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    subheader = models.CharField(max_length=200, blank=True)
    body = HTMLField(blank=True)
    tag_id = models.CharField(max_length=200,
                              help_text="displayed as url fragment",
                              blank=False)
    show_back_to_top = models.BooleanField(default=True)


class CarouselPluginModel(CMSPlugin):
    background_color = models.CharField(max_length=7, blank=True)

    def copy_relations(self, oldinstance):
        for content in oldinstance.carouselcontent_set.all():
            content.pk = None
            content.carousel = self
            content.save()


class CarouselContent(models.Model):
    background_color = models.CharField(max_length=7, blank=True)
    carousel = models.ForeignKey(CarouselPluginModel)
    body = HTMLField(blank=True)
    page = models.ForeignKey(Page, blank=True, null=True)
    sorting = models.IntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['sorting']
