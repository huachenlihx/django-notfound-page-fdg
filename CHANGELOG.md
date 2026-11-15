# Changelog

## 0.1.0 — Initial release

- Reusable, configurable Django 404 page with an HTTP 404 response.
- Optional JSON 404 responses through an explicit root URL handler.
- Django system checks for configuration mistakes and home links.
- Automatically selects a valid backend home URL (root or Django Admin) and hides the link when neither is available.
- Template customization through Django's standard template loaders.
- Initial package distribution as `django-notfound-page-fdg`.
- Accepts lazy strings (`gettext_lazy`, `reverse_lazy`) for text settings and `HOME_URL`, and an integer `ERROR_CODE`.
- Accepts modern CSS color syntax (`rgb(r g b / a)`, `oklch()`, `hwb()`, `var(--name)`).
