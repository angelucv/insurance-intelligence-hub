from django.contrib import admin
from django.urls import path

from core.views import upload_policies

urlpatterns = [
    path("admin/upload-policies/", upload_policies),
    path("admin/", admin.site.urls),
]
