from django.core import checks
from django.test import SimpleTestCase, override_settings

from notfound_page.conf import resolve_home_url


class DefaultHandlerTests(SimpleTestCase):
    """Works with Django's built-in handler: only INSTALLED_APPS needed."""

    def test_returns_404_with_custom_page(self):
        r = self.client.get("/abc")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "Page not found", status_code=404)
        self.assertContains(r, 'href="/admin/"', status_code=404)

    def test_auto_prefers_admin_when_root_is_missing(self):
        self.assertEqual(resolve_home_url("auto"), "/admin/")
        self.assertContains(self.client.get("/missing"), 'href="/admin/"', status_code=404)
        self.assertNotIn("notfound_page.W002", {issue.id for issue in checks.run_checks()})

    @override_settings(ROOT_URLCONF="tests.urls_root")
    def test_auto_prefers_existing_root_over_admin(self):
        self.assertEqual(resolve_home_url("auto"), "/")
        self.assertContains(self.client.get("/missing"), 'href="/"', status_code=404)

    @override_settings(ROOT_URLCONF="tests.urls_empty")
    def test_auto_hides_link_when_no_home_route_exists(self):
        self.assertEqual(resolve_home_url("auto"), "")
        response = self.client.get("/missing")
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, 'class="nf-home"', status_code=404)

    @override_settings(NOTFOUND_PAGE={"HOME_URL": "unknown:name"})
    def test_unresolvable_explicit_url_does_not_link_to_missing_root(self):
        response = self.client.get("/missing")
        self.assertNotContains(response, 'class="nf-home"', status_code=404)
        self.assertIn("notfound_page.W003", {issue.id for issue in checks.run_checks()})

    @override_settings(NOTFOUND_PAGE={"HOME_URL": "/admin/", "HOME_LABEL": "Back to Admin"})
    def test_configurable_home_url_and_label(self):
        r = self.client.get("/abc")
        self.assertContains(r, 'href="/admin/"', status_code=404)
        self.assertContains(r, "Back to Admin", status_code=404)

    @override_settings(NOTFOUND_PAGE={"HOME_URL": "admin:index"})
    def test_url_name_is_reversed(self):
        self.assertContains(self.client.get("/abc"), 'href="/admin/"', status_code=404)

    @override_settings(NOTFOUND_PAGE={"SHOW_HOME_LINK": False})
    def test_home_link_can_be_hidden(self):
        self.assertNotContains(self.client.get("/abc"), "nf-home\"", status_code=404)

    @override_settings(NOTFOUND_PAGE={"HEADING": "<b>x</b>"})
    def test_text_is_escaped(self):
        r = self.client.get("/abc")
        self.assertNotContains(r, "<b>x</b>", status_code=404)

    @override_settings(NOTFOUND_PAGE={"SHOW_REQUEST_PATH": True})
    def test_request_path_optional_and_escaped(self):
        r = self.client.get("/<script>")
        self.assertNotContains(r, "<script>", status_code=404)
        self.assertContains(r, "/%3Cscript%3E", status_code=404)  # Django percent-encodes the path

    @override_settings(NOTFOUND_PAGE={"PRIMARY_COLOR": "#ff0000"})
    def test_colors(self):
        self.assertContains(self.client.get("/abc"), "#ff0000", status_code=404)


@override_settings(ROOT_URLCONF="tests.urls_handler")
class CustomHandlerTests(SimpleTestCase):
    def test_html_by_default(self):
        r = self.client.get("/abc")
        self.assertEqual(r.status_code, 404)
        self.assertIn("text/html", r["Content-Type"])

    @override_settings(NOTFOUND_PAGE={"API_PATH_PREFIXES": ["/api/"]})
    def test_json_for_api_prefix(self):
        r = self.client.get("/api/nope")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {"detail": "Not found."})

    def test_json_when_client_asks_for_json(self):
        r = self.client.get("/abc", HTTP_ACCEPT="application/json")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {"detail": "Not found."})

    @override_settings(NOTFOUND_PAGE={"JSON_FOR_JSON_REQUESTS": False})
    def test_json_negotiation_can_be_disabled(self):
        r = self.client.get("/abc", HTTP_ACCEPT="application/json")
        self.assertIn("text/html", r["Content-Type"])


class HelperAndCheckTests(SimpleTestCase):
    def test_resolve_home_url(self):
        self.assertEqual(resolve_home_url("/x/"), "/x/")
        self.assertEqual(resolve_home_url("https://e.com"), "https://e.com")
        self.assertEqual(resolve_home_url("admin:index"), "/admin/")
        self.assertEqual(resolve_home_url("nope:nope"), "")
        self.assertEqual(resolve_home_url(None), "")

    def _ids(self):
        return {i.id for i in checks.run_checks() if i.id.startswith("notfound_page")}

    @override_settings(NOTFOUND_PAGE={"HOME_URL": "/does-not-exist/"})
    def test_warns_when_home_does_not_resolve(self):
        self.assertIn("notfound_page.W002", self._ids())

    @override_settings(NOTFOUND_PAGE={"HOME_URL": "/admin/"})
    def test_no_warning_when_home_resolves(self):
        self.assertNotIn("notfound_page.W002", self._ids())

    @override_settings(NOTFOUND_PAGE={"NOPE": 1})
    def test_unknown_key(self):
        self.assertIn("notfound_page.W001", self._ids())

    @override_settings(NOTFOUND_PAGE={"PRIMARY_COLOR": "red;}</style>"})
    def test_bad_color(self):
        self.assertIn("notfound_page.E002", self._ids())


class AdditionalTests(SimpleTestCase):
    @override_settings(NOTFOUND_PAGE={"HOME_URL": "//example.com"})
    def test_protocol_relative_home_is_not_used(self):
        self.assertEqual(resolve_home_url("//example.com"), "")

    @override_settings(NOTFOUND_PAGE={"API_PATH_PREFIXES": "api"})
    def test_invalid_json_prefixes_detected(self):
        issues = {i.id for i in checks.run_checks()}
        self.assertIn("notfound_page.E005", issues)

    @override_settings(NOTFOUND_PAGE={"SHOW_HOME_LINK": "yes"})
    def test_boolean_type_is_checked(self):
        issues = {i.id for i in checks.run_checks()}
        self.assertIn("notfound_page.E003", issues)


def _ids():
    return {i.id for i in checks.run_checks() if i.id.startswith("notfound_page")}


class ColorValidationTests(SimpleTestCase):
    def test_accepted_colors(self):
        good = [
            "#fff", "#ffff", "#2563eb", "#2563eb80", "rebeccapurple", "RED",
            "rgb(37, 99, 235)", "rgba(37,99,235,.5)", "hsl(220 90% 56%)",
            "rgb(37 99 235 / 50%)", "oklch(60% 0.2 250)", "hwb(220 10% 10%)",
            "var(--brand)",
        ]
        for value in good:
            with self.subTest(value=value), override_settings(
                NOTFOUND_PAGE={"PRIMARY_COLOR": value, "HOME_URL": "/admin/"}
            ):
                self.assertNotIn("notfound_page.E002", _ids())

    def test_rejected_colors(self):
        bad = [
            "#12345", "#1234567", "#ggg", "red;}</style>", "url(x)", "rgb(1,2,3);x",
            "rgb(var(--a))", "expression(alert(1))", "", None, 123,
        ]
        for value in bad:
            with self.subTest(value=value), override_settings(
                NOTFOUND_PAGE={"PRIMARY_COLOR": value, "HOME_URL": "/admin/"}
            ):
                self.assertIn("notfound_page.E002", _ids())

    @override_settings(NOTFOUND_PAGE={"PRIMARY_COLOR": "rgb(37 99 235 / 50%)"})
    def test_modern_color_is_rendered(self):
        self.assertContains(self.client.get("/abc"), "rgb(37 99 235 / 50%)", status_code=404)


class LazyAndTypeTests(SimpleTestCase):
    @override_settings(NOTFOUND_PAGE={"ERROR_CODE": 404, "HOME_URL": "/admin/"})
    def test_integer_error_code_allowed(self):
        self.assertNotIn("notfound_page.E004", _ids())
        self.assertContains(self.client.get("/abc"), ">404<", status_code=404)

    @override_settings(NOTFOUND_PAGE={"ERROR_CODE": True})
    def test_bool_error_code_rejected(self):
        self.assertIn("notfound_page.E004", _ids())

    @override_settings(NOTFOUND_PAGE={"ERROR_CODE": 4.5})
    def test_float_error_code_rejected(self):
        self.assertIn("notfound_page.E004", _ids())

    def test_reverse_lazy_home_url(self):
        from django.urls import reverse_lazy

        with override_settings(NOTFOUND_PAGE={"HOME_URL": reverse_lazy("admin:index")}):
            self.assertNotIn("notfound_page.E006", _ids())
            self.assertNotIn("notfound_page.W002", _ids())
            self.assertEqual(resolve_home_url(reverse_lazy("admin:index")), "/admin/")
            self.assertContains(self.client.get("/abc"), 'href="/admin/"', status_code=404)

    def test_lazy_text_settings(self):
        from django.utils.translation import gettext_lazy

        with override_settings(
            NOTFOUND_PAGE={"HEADING": gettext_lazy("Lost?"), "HOME_URL": "/admin/"}
        ):
            self.assertNotIn("notfound_page.E004", _ids())
            self.assertContains(self.client.get("/abc"), "<h1>Lost?</h1>", status_code=404)

    @override_settings(ROOT_URLCONF="tests.urls_handler")
    def test_lazy_json_message(self):
        from django.utils.translation import gettext_lazy

        with override_settings(NOTFOUND_PAGE={"JSON_MESSAGE": gettext_lazy("Gone.")}):
            r = self.client.get("/abc", HTTP_ACCEPT="application/json")
            self.assertEqual(r.status_code, 404)
            self.assertEqual(r.json(), {"detail": "Gone."})

    @override_settings(NOTFOUND_PAGE={"HOME_LABEL": 5})
    def test_non_text_setting_rejected(self):
        self.assertIn("notfound_page.E004", _ids())
