import logging
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response

error_logger = logging.getLogger("error")


class GeneralResponse(Response):
    def __init__(self, data=None, status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        payload = {"message": _(data)}
        Response.__init__(self, payload, status, template_name, headers, exception, content_type)


class ErrorResponse(Response):
    def __init__(self, data=None, status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        try:
            key = next(iter(data))
            error = data[key][0]
            if key == "non_field_errors" or key == 'email':
                payload = {"message": str(_(error))}
            else:
                payload = {"message": str(_(key)) + " " + str(_(error))}

            Response.__init__(self, payload, status, template_name, headers, exception, content_type)
        except Exception as e:
            error_logger.error("Error %s occured in ErrorResponse" % e)
            payload = {"message": data}
            Response.__init__(self, payload, status, template_name, headers, exception, content_type)


class ErrorListResponse(Response):
    def __init__(self, field_erros: dict):
        super(ErrorListResponse, self).__init__(
            {
                field: errors if isinstance(errors, list) else [errors]
                for field, errors in field_erros.items()
            },
            status=400
        )
