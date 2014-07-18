from cms.templatetags.cms_tags import Placeholder
from django import template

register = template.Library()


class RenderHiddenPlaceholder(Placeholder):
    name = 'render_hidden_placeholder'

    def render_tag(self, context, name, extra_bits, nodelist=None):
        # never render in edit mode
        if not 'request' in context:
            return ''
        request = context['request']
        edit_mode = getattr(request, 'toolbar', None) and getattr(request.toolbar, 'edit_mode')
        if edit_mode:
            return ''
        # always render when not in edit mode
        context.push()
        context['show_hidden'] = True
        retval = super(RenderHiddenPlaceholder, self).render_tag(context, name, extra_bits, nodelist=nodelist)
        context.pop()
        return retval


register.tag(RenderHiddenPlaceholder)
