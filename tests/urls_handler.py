from django.contrib import admin
from django.urls import path

urlpatterns = [path("admin/", admin.site.urls)]
handler404 = "notfound_page.views.page_not_found"
