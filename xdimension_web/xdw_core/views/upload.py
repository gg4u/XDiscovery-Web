from __future__ import absolute_import

from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from jfu.http import upload_receive, UploadResponse

from ..maps import save_map
from ..models import Map


@require_POST
def upload_multi(request):
    file_data = upload_receive(request)
    obj = Map(map_data=file_data.read())
    obj = save_map(obj)
    result = {'name': obj.title, 'url': reverse('admin:xdw_core_map_change',
                                                args=[obj.pk])}
    return UploadResponse(request, result)
