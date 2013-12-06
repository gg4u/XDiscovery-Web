from __future__ import absolute_import

from django import forms

from .models import CarouselContent, BoxPluginModel


class PageLinkMixIn(object):

    def set_choices(self):
        choices = [self.fields['page'].choices.__iter__().next()]
        for page in self.fields['page'].queryset:
            choices.append(
                (page.id, ''.join(['-'*page.level, page.__unicode__()]))
            )
        self.fields['page'].choices = choices


class CarouselContentForm(PageLinkMixIn, forms.ModelForm):
    class Meta:
        model = CarouselContent

    def __init__(self, *args, **kwargs):
        super(CarouselContentForm, self).__init__(*args, **kwargs)
        self.set_choices()


class BoxForm(PageLinkMixIn, forms.ModelForm):
    class Meta:
        model = BoxPluginModel

    def __init__(self, *args, **kwargs):
        super(BoxForm, self).__init__(*args, **kwargs)
        self.set_choices()
