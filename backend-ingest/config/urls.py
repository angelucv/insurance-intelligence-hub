from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from core.views import upload_policies

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="admin:index", permanent=False)),
    path("admin/upload-policies/", upload_policies),
    path("admin/", admin.site.urls),
]
