"""Template tags exposing the reusable 404 page configuration."""
from django import template

from ..conf import get_config, resolve_home_url

register = template.Library()


@register.simple_tag(takes_context=True)
def notfound_context(context):
    """Expose settings to the template without requiring a custom handler."""
    cfg = get_config()
    request = context.get("request")
    request_path = context.get("request_path", "")
    if not request_path and request is not None:
        request_path = request.path
    home_url = resolve_home_url(cfg["HOME_URL"])
    return {
        "home_url": home_url,
        "home_label": cfg["HOME_LABEL"],
        "show_home_link": cfg["SHOW_HOME_LINK"] and bool(home_url),
        "site_name": cfg["SITE_NAME"],
        "title": cfg["TITLE"],
        "error_code": cfg["ERROR_CODE"],
        "heading": cfg["HEADING"],
        "message": cfg["MESSAGE"],
        "language": cfg["LANGUAGE_CODE"],
        "show_request_path": cfg["SHOW_REQUEST_PATH"],
        "request_path": request_path,
        "primary": cfg["PRIMARY_COLOR"],
        "primary_hover": cfg["PRIMARY_HOVER_COLOR"],
        "background": cfg["BACKGROUND_COLOR"],
        "text": cfg["TEXT_COLOR"],
    }
