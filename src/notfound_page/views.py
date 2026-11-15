"""Optional HTTP 404 handler with API-friendly JSON responses."""
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist

from .conf import get_config


def _wants_json(request, cfg):
    prefixes = cfg["API_PATH_PREFIXES"]
    if isinstance(prefixes, (tuple, list)) and any(
        isinstance(prefix, str) and request.path.startswith(prefix) for prefix in prefixes
    ):
        return True
    if cfg["JSON_FOR_JSON_REQUESTS"]:
        accept = request.headers.get("Accept", "")
        return "application/json" in accept and "text/html" not in accept
    return False


def page_not_found(request, exception=None, template_name=None):
    """Drop-in Django handler404; always returns HTTP 404.

    In the project's root urls.py:
        handler404 = "notfound_page.views.page_not_found"
    """
    cfg = get_config()
    if _wants_json(request, cfg):
        return JsonResponse({"detail": str(cfg["JSON_MESSAGE"])}, status=404)
    try:
        return render(
            request,
            template_name or cfg["TEMPLATE_NAME"],
            {"request_path": request.path},
            status=404,
        )
    except TemplateDoesNotExist:
        return HttpResponseNotFound("<h1>Not Found</h1>", content_type="text/html")
