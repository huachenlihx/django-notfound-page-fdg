"""Django system checks for notfound_page configuration."""
import re

from django.core.checks import Error, Warning, register
from django.urls import NoReverseMatch, Resolver404, resolve, reverse

from .conf import (
    BOOL_KEYS, COLOR_KEYS, DEFAULTS, SETTING_NAME, TEXT_KEYS,
    as_text, get_config, get_user_settings, is_external, is_path_style,
)

# Conservative CSS color forms, so arbitrary CSS can never be injected from settings:
# hex (3/4/6/8 digits), named colors, color functions (legacy and modern space/slash
# syntax, e.g. "rgb(37 99 235 / 50%)", "oklch(60% 0.2 250)") and var(--name).
# Function arguments cannot contain parentheses, quotes, braces or semicolons.
_COLOR_FUNCTIONS = "rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch"
_SAFE_COLOR = re.compile(
    r"#(?:[0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})"
    r"|[a-z]+"
    rf"|(?:{_COLOR_FUNCTIONS})\([a-z0-9_.,%\s/+-]+\)"
    r"|var\(--[a-z0-9_-]+\)",
    re.IGNORECASE,
)


@register()
def check_notfound_page(app_configs, **kwargs):
    issues = []
    raw = get_user_settings()
    if not isinstance(raw, dict):
        return [Error(f"{SETTING_NAME} must be a dict.", id="notfound_page.E001")]

    for key in raw:
        if key not in DEFAULTS:
            issues.append(Warning(
                f"Unknown key {key!r} in {SETTING_NAME}.",
                hint="Valid keys: " + ", ".join(sorted(DEFAULTS)),
                id="notfound_page.W001",
            ))

    cfg = get_config()
    for key in COLOR_KEYS:
        value = cfg[key]
        if not isinstance(value, str) or not _SAFE_COLOR.fullmatch(value):
            issues.append(Error(
                f"{SETTING_NAME}[{key!r}] is not a supported CSS color.",
                hint="Use #RRGGBB, a named color, rgb()/hsl()/hwb()/lab()/lch()/oklab()/oklch(), or var(--name).",
                id="notfound_page.E002",
            ))
    for key in BOOL_KEYS:
        if not isinstance(cfg[key], bool):
            issues.append(Error(f"{SETTING_NAME}[{key!r}] must be a boolean.", id="notfound_page.E003"))
    for key in TEXT_KEYS:
        if as_text(cfg[key]) is None:
            issues.append(Error(f"{SETTING_NAME}[{key!r}] must be a string.", id="notfound_page.E004"))
    code = cfg["ERROR_CODE"]
    if as_text(code) is None and (isinstance(code, bool) or not isinstance(code, int)):
        issues.append(Error(
            f"{SETTING_NAME}['ERROR_CODE'] must be a string or an integer.", id="notfound_page.E004"
        ))
    prefixes = cfg["API_PATH_PREFIXES"]
    if not isinstance(prefixes, (list, tuple)) or any(
        not isinstance(prefix, str) or not prefix.startswith("/") for prefix in prefixes
    ):
        issues.append(Error(
            f"{SETTING_NAME}['API_PATH_PREFIXES'] must be a list/tuple of paths starting with '/'.",
            id="notfound_page.E005",
        ))

    home = as_text(cfg["HOME_URL"])
    if home is None:
        issues.append(Error(f"{SETTING_NAME}['HOME_URL'] must be a string.", id="notfound_page.E006"))
    elif cfg["SHOW_HOME_LINK"] is True and home != "auto":
        if is_path_style(home):
            path = home.split("?", 1)[0].split("#", 1)[0]
            try:
                resolve(path)
            except Resolver404:
                issues.append(Warning(
                    f"HOME_URL {home!r} does not match a Django URL route.",
                    hint="Use an existing route, such as '/admin/'.",
                    id="notfound_page.W002",
                ))
            except Exception:
                pass  # Django will report broken URLconfs separately.
        elif not is_external(home):
            try:
                reverse(home)
            except NoReverseMatch:
                issues.append(Warning(
                    f"HOME_URL {home!r} is not a path, full http(s) URL, or reversible URL name.",
                    hint="Use '/admin/', '/', or 'admin:index'.",
                    id="notfound_page.W003",
                ))
            except Exception:
                pass
    return issues
