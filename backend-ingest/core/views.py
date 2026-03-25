"""Vistas internas: carga de maestros en PostgreSQL (validación hub-contracts)."""

from __future__ import annotations

import json

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse

from core.forms import PolicyFileForm
from core.ingest_service import ingest_policies_file


@staff_member_required
def upload_policies(request):  # noqa: ANN001
    """Persiste CSV/XLSX; plantilla integrada en el sitio Admin (base_site)."""
    context = {
        **admin.site.each_context(request),
        "title": "Carga de pólizas (CSV / Excel)",
        "form": PolicyFileForm(),
        "error": None,
        "result_json": None,
    }
    if request.method == "POST":
        form = PolicyFileForm(request.POST, request.FILES)
        context["form"] = form
        if form.is_valid():
            f = request.FILES["file"]
            content = f.read()
            try:
                result = ingest_policies_file(content, f.name, source="django")
                context["result_json"] = json.dumps(result, indent=2, ensure_ascii=False)
            except Exception as e:
                context["error"] = str(e)
    return TemplateResponse(request, "admin/upload_policies.html", context)
