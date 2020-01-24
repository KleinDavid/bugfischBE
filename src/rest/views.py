from rest_framework.generics import ListCreateAPIView
from services.requestService import RequestService


class ExecuteAction(ListCreateAPIView):
    requestService = RequestService()

    def post(self, request):
        return self.requestService.handleExecuteAction(request)
