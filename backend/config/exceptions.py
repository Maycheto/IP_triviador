from django.http import JsonResponse
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    data = response.data
    if isinstance(data, dict) and list(data.keys()) == ["detail"]:
        errors = {"detail": [data["detail"]]}
    elif isinstance(data, dict):
        errors = data
    else:
        errors = {"non_field_errors": data}

    response.data = {"errors": errors}
    return response


def csrf_failure(request, reason=""):
    return JsonResponse({"errors": {"detail": [f"CSRF Failed: {reason}"]}}, status=403)
