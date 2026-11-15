"""Configuration helpers for the NOTFOUND_PAGE Django setting."""
from django.conf import settings
from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from django.utils.functional import Promise

SETTING_NAME = "NOTFOUND_PAGE"

DEFAULTS = {
    "HOME_URL": "auto",
    "HOME_LABEL": "Back to home",
    "SHOW_HOME_LINK": True,
    "SITE_NAME": "",
    "TITLE": "404 - Page not found",
    "ERROR_CODE": "404",
    "HEADING": "Page not found",
    "MESSAGE": "The page you requested does not exist or has moved.",
    "LANGUAGE_CODE": "en",
    "SHOW_REQUEST_PATH": False,
    "PRIMARY_COLOR": "#2563eb",
    "PRIMARY_HOVER_COLOR": "#1d4ed8",
    "BACKGROUND_COLOR": "#f8fafc",
    "TEXT_COLOR": "#1e293b",
    "TEMPLATE_NAME": "notfound_page/404.html",
    "API_PATH_PREFIXES": (),
    "JSON_FOR_JSON_REQUESTS": True,
    "JSON_MESSAGE": "Not found.",
}

COLOR_KEYS = ("PRIMARY_COLOR", "PRIMARY_HOVER_COLOR", "BACKGROUND_COLOR", "TEXT_COLOR")
TEXT_KEYS = (
    "HOME_LABEL", "SITE_NAME", "TITLE", "HEADING",
    "MESSAGE", "LANGUAGE_CODE", "TEMPLATE_NAME", "JSON_MESSAGE",
)
BOOL_KEYS = ("SHOW_HOME_LINK", "SHOW_REQUEST_PATH", "JSON_FOR_JSON_REQUESTS")


def as_text(value):
    """Return ``value`` as ``str``, or ``None`` if it is not text.

    Accepts plain strings and lazy strings such as ``gettext_lazy(...)`` and
    ``reverse_lazy(...)``.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, Promise):
        try:
            return str(value)
        except Exception:
            return None
    return None


def get_user_settings():
    value = getattr(settings, SETTING_NAME, {})
    return {} if value is None else value


def get_config():
    user = get_user_settings()
    return {**DEFAULTS, **user} if isinstance(user, dict) else DEFAULTS.copy()


def is_path_style(value):
    return isinstance(value, str) and value.startswith("/") and not value.startswith("//")


def is_external(value):
    return isinstance(value, str) and value.startswith(("http://", "https://"))


def _route_exists(path):
    """Check that a local path is recognized by the project's URLconf."""
    try:
        resolve(path.split("?", 1)[0].split("#", 1)[0])
        return True
    except (Resolver404, ValueError):
        return False


def resolve_home_url(value):
    """Resolve an explicit destination, or automatically find a backend home.

    In auto mode, prefer an actual root route, then Django admin when installed.
    An empty result means there is no safe destination, so the template hides
    the link rather than sending users to another 404 page.
    """
    value = as_text(value)
    if value == "auto":
        if _route_exists("/"):
            return "/"
        try:
            return reverse("admin:index")
        except NoReverseMatch:
            return ""
    if not value or value.startswith("//"):
        return ""
    if is_path_style(value) or is_external(value):
        return value
    try:
        return reverse(value)
    except NoReverseMatch:
        return ""
