from django.http import HttpResponse
from django.urls import path

urlpatterns = [path("", lambda request: HttpResponse("Backend home"), name="home")]
