from cms.models.pluginmodel import CMSPlugin
from djangocms_text_ckeditor.fields import HTMLField
from django.db import models


class BoxPluginModel(CMSPlugin):
    title = models.TextField(blank=True)
    body = HTMLField(blank=True)
    # future-proof
    more = models.CharField(max_length=500, blank=True)


class AbstractPluginModel(CMSPlugin):
    body = models.TextField(blank=True)
