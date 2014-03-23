

class PartialResponseMiddleware(object):

    def process_template_response(self, request, response):
        if request.GET.get('angular') or request.is_ajax():
            response.template_name = 'xdw_web/cms_templates/angular.html'
        return response
