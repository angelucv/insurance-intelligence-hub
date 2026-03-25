"""Vistas internas: carga de maestros en PostgreSQL (validación hub-contracts)."""

from __future__ import annotations

import json

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from core.forms import PolicyFileForm
from core.ingest_service import ingest_policies_file


@staff_member_required
def upload_policies(request):  # noqa: ANN001
    """Persiste CSV/XLSX en la misma BD que la API (validación Pydantic en el proceso Django)."""
    context: dict = {"form": PolicyFileForm(), "result": None, "error": None}
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
    return render(request, "core/upload_policies.html", context)
