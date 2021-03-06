import logging

from rest_framework.response import Response
from rest_framework.views import APIView


cli_error_logger = logging.getLogger("cli_error")
OKResponse = Response("OK")


class ErrorsView(APIView):
    def post(self, request):
        cli_error_logger.info(request.data)
        return OKResponse
