import logging
import traceback

from django.utils.translation import ugettext_lazy
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed

from common.response import GeneralResponse

error_logger = logging.getLogger("error")


def api_exception_handler(exc, context):
    # noinspection PyProtectedMember
    request = context['request']._request
    error_logger.error("""
API Error on {}: {}
Exception: '{}: {}'
{}
Request Info:
GET: {}
POST: {}
USER: {}
META: {}
""".strip().format(request.method, request.path, type(exc), str(exc), traceback.format_exc(), request.GET, request.POST,
                   request.user.id, request.META))

    if type(exc) is AuthenticationFailed:
        return GeneralResponse("Your token is not valid. Please login first", status=status.HTTP_401_UNAUTHORIZED)

    return GeneralResponse(
        ugettext_lazy("Sorry about this inconvenience, there is a problem in our side, we'll fix it soon"),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
