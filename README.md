# Django Notfound Page FDG

Reusable, configurable **404 – Page Not Found** pages for Django applications, including existing projects and new projects. The package supplies a simple HTML page and optional JSON responses for APIs. It has no database models or migrations.

- **PyPI distribution:** `django-notfound-page-fdg`
- **Import / Django app:** `notfound_page`
- **Initial version:** `0.1.0`
- **Author:** Hua Chen
- **License:** MIT
- **Python:** 3.9+
- **Django:** 4.2 to 6.x (compatible Python/Django combinations)

The HTML and JSON error responses use the actual **HTTP 404 status**, not a redirect or HTTP 200. The package uses Django's built-in 404 handling rather than replacing its URL router.

## Installation

```bash
python -m pip install django-notfound-page-fdg
```

Add the app to your existing `INSTALLED_APPS` (preferably **after** apps with their own `404.html`):

```python
INSTALLED_APPS = [
    # ... other installed apps ...
    "notfound_page.apps.NotFoundPageConfig",
]
```

Ensure your Django template engine uses `"APP_DIRS": True` or explicitly includes the app-template loader. **Do not replace your existing `TEMPLATES` configuration.**

For normal HTML 404 pages, this is all that is needed. With `DEBUG=False`, Django's default handler looks up `404.html`, which the package provides. The package does not add URL patterns or middleware.

**Important for existing projects:** If your project already has `templates/404.html`, Django may use your existing template instead. This is intentional: project templates take precedence. You can keep your existing page, remove it to use the package default, or extend `notfound_page/404.html` for customization. If another installed app has a `404.html`, template-loader order determines which one wins.

## Back to backend home

By default, `HOME_URL` is `"auto"`: the package links to `/` if the backend has a matching root route, otherwise to Django Admin (`admin:index`) if available. If neither exists, the home button is hidden rather than leading to another 404. This makes the default work for API-only and admin-only Django installations without assuming that `/` is a homepage.

To explicitly choose your backend home, set `NOTFOUND_PAGE` in the consuming project's `settings.py`:

```python
NOTFOUND_PAGE = {
    "HOME_URL": "/admin/",  # or "/" if your backend has a root homepage
    "HOME_LABEL": "Back to Backend Home",
    "SITE_NAME": "Appointment API",
}
```

`HOME_URL` accepts `"auto"`, a local path, an HTTP(S) URL, or a named Django URL such as `"admin:index"`. Using `"admin:index"` avoids hard-coding the Admin URL. `python manage.py check` warns when an explicitly configured path is not recognized by Django URL routing (a warning, not an installation blocker). If an explicit named route cannot be reversed, its link is hidden instead of falling back to a nonexistent `/`.

The home link stays on the backend if you use a relative path like `/admin/` or `/`. This package does **not** modify the Next.js/React frontend.

## Configuration

All options live under the `NOTFOUND_PAGE` dictionary. Unspecified values use defaults.

| Key | Default | Description |
| --- | --- | --- |
| `HOME_URL` | `"auto"` | Automatically choose an existing backend `/` route or Django Admin; hide link if neither exists. Can also be a path, HTTP(S) URL, or Django URL name |
| `HOME_LABEL` | `"Back to home"` | Button label |
| `SHOW_HOME_LINK` | `True` | Show or hide the button |
| `SITE_NAME` | `""` | Optional site label |
| `TITLE` | `"404 - Page not found"` | Browser title |
| `ERROR_CODE` | `"404"` | Large display code |
| `HEADING` | `"Page not found"` | Main page heading |
| `MESSAGE` | `"The page you requested does not exist or has moved."` | Description |
| `LANGUAGE_CODE` | `"en"` | HTML language attribute |
| `SHOW_REQUEST_PATH` | `False` | Show the request path in HTML, escaped by Django |
| `PRIMARY_COLOR` | `"#2563eb"` | Title and button color |
| `PRIMARY_HOVER_COLOR` | `"#1d4ed8"` | Button hover color |
| `BACKGROUND_COLOR` | `"#f8fafc"` | Page background |
| `TEXT_COLOR` | `"#1e293b"` | Text color |
| `TEMPLATE_NAME` | `"notfound_page/404.html"` | Template for optional handler below |
| `API_PATH_PREFIXES` | `()` | Paths served as JSON by optional handler |
| `JSON_FOR_JSON_REQUESTS` | `True` | JSON for `Accept: application/json` with no HTML preference |
| `JSON_MESSAGE` | `"Not found."` | JSON response's `detail` value |

Django's system checks report unexpected keys and invalid configurations. Color values are restricted to safe CSS forms so no arbitrary CSS can be injected: hex (`#RGB`, `#RGBA`, `#RRGGBB`, `#RRGGBBAA`), named colors, the functions `rgb()`, `rgba()`, `hsl()`, `hsla()`, `hwb()`, `lab()`, `lch()`, `oklab()` and `oklch()` (both comma and modern space/slash syntax, e.g. `rgb(37 99 235 / 50%)`), and `var(--name)`. Anything else is reported as error `notfound_page.E002`.

Text settings (`HEADING`, `MESSAGE`, `HOME_LABEL`, ...) may be plain strings or lazy strings such as `gettext_lazy("...")`, so the page can be translated. `HOME_URL` may be a string or `reverse_lazy("admin:index")`. `ERROR_CODE` may be a string or an integer.

## Optional API JSON 404 responses

The **built-in Django 404 handler always returns HTML**. To enable the package's optional JSON behavior, set this in the **root URLconf** (often `<project>/urls.py`):

```python
handler404 = "notfound_page.views.page_not_found"
```

Configure the API route prefixes in `settings.py`:

```python
NOTFOUND_PAGE = {
    "HOME_URL": "admin:index",
    "API_PATH_PREFIXES": ["/api/"],
    "JSON_FOR_JSON_REQUESTS": True,
}
```

Unknown `/api/...` paths now receive:

```json
{"detail": "Not found."}
```

with HTTP **404**. HTML browser routes continue to receive the HTML template. Clients sending `Accept: application/json` (without `text/html`) also receive JSON. These settings apply to **unmatched Django routes**, not to HTTP 404 responses generated independently by individual Django REST Framework views.

Note: `handler404` only takes effect when `DEBUG=False`. If you already define a custom `handler404`, choose which handler to use, or delegate explicitly rather than overwriting it without review.

## Customize the HTML template

To override the default package page, create `templates/404.html` in your project, or create a project-specific template extending the package template:

```django
{% extends "notfound_page/404.html" %}
{% block extra_styles %}
body { font-family: Georgia, serif; }
{% endblock %}
{% block content %}
<h1>Sorry, this backend page could not be found.</h1>
<a href="/admin/">Back to Admin</a>
{% endblock %}
```

The shipped template exposes blocks `title`, `extra_styles` and `content`, plus `{% load notfound_page %}{% notfound_context as nf %}` for configuration values such as `nf.home_url` and `nf.heading`.

## Local testing

Set `DEBUG=False` and configure `ALLOWED_HOSTS` for local requests in your project's settings. For instance, if your settings use `DJANGO_DEBUG` and `DJANGO_ALLOWED_HOSTS`:

```dotenv
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Then:

```bash
python manage.py check
python manage.py runserver
curl -i http://127.0.0.1:8000/abc
```

The response should have `HTTP/1.1 404 Not Found` and the custom page. If `/admin/` is configured, follow the link to the backend admin. Restore normal local debugging settings afterward.

If nginx or another reverse proxy intercepts missing paths **before Django**, that server's 404 is outside this package's control.

## Development and testing

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
DJANGO_SETTINGS_MODULE=tests.settings python -m django check
python -m django test tests --settings=tests.settings --verbosity 2
```

GitHub Actions CI (`.github/workflows/ci.yml`) tests compatible combinations of Python 3.9–3.13 and Django 4.2, 5.2, and 6.x. The matrix is provided for validation; passing results should be confirmed in your own repository.

## Publishing

Before publishing, make sure the intended package name is available on PyPI and create the corresponding GitHub repository if desired. The GitHub links in `pyproject.toml` are intended project addresses, **not verified existing repositories**.

```bash
python -m pip install --upgrade build twine
rm -rf dist/ build/
python -m build
python -m twine check dist/*
```

Inspect the wheel and sdist, install the wheel in a clean environment, and run the test suite before uploading to [TestPyPI](https://test.pypi.org/) and then [PyPI](https://pypi.org/). Confirm the package metadata lists `django-notfound-page-fdg`.

For the initial release, `src/notfound_page/__init__.py` declares `__version__ = "0.1.0"`. Bump the version for each subsequent release; PyPI does not permit replacing an existing uploaded distribution file.

## Project links

- GitHub repository (create before publishing): https://github.com/huachenlihx/django-notfound-page-fdg
- Issues (after repository creation): https://github.com/huachenlihx/django-notfound-page-fdg/issues
- PyPI project (after publication): https://pypi.org/project/django-notfound-page-fdg/

## License and contact

MIT License — Copyright (c) 2026 Hua Chen. See the [LICENSE](https://github.com/huachenlihx/django-notfound-page-fdg/blob/main/LICENSE) file.

Email: `huachenlihx@gmail.com`
