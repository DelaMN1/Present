from django.contrib import admin
from django.urls import include, path

from accounts.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("", include("accounts.urls")),
    path("", include("courses.urls")),
]

handler403 = "django.views.defaults.permission_denied"
