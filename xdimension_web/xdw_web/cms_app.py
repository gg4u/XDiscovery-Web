from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

class SPAhook(CMSApp):
    name = _("SPA Apphook")
    urls = ["xdimension_web.xdw_web.urls"]

apphook_pool.register(SPAhook)
