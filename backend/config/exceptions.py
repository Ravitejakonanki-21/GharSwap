from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    detail = response.data
    if isinstance(detail, dict) and "detail" in detail and len(detail) == 1:
        message = detail["detail"]
        errors = None
    else:
        message = "Request could not be processed."
        errors = detail

    payload = {"error": True, "message": message, "errors": errors}
    response.data = payload
    return response
