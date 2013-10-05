from rest_framework.viewsets import ViewSet
from rest_framework.response import Response


class StubViewSet(ViewSet):

    def list(self, request):
        return Response([])