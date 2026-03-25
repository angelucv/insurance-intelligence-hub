from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from core.views import upload_policies

admin.site.site_header = "Insurance Intelligence Hub"
admin.site.site_title = "IIHub · Seguros La Fe"
admin.site.index_title = "Administración"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="admin:index", permanent=False)),
    path("admin/upload-policies/", upload_policies, name="upload_policies"),
    path("admin/", admin.site.urls),
]
