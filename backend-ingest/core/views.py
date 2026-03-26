"""Vistas internas: carga de maestros en PostgreSQL (validación hub-contracts)."""

from __future__ import annotations

import json

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse

from core.forms import ClaimFileForm, PolicyFileForm
from core.ingest_service import ingest_claims_file, ingest_policies_file


def _result_payload(result: dict) -> dict[str, object]:
    """Serialización para plantilla: resumen estructurado + JSON completo plegable."""
    return {
        "ingest_result": result,
        "result_json": json.dumps(result, indent=2, ensure_ascii=False),
    }


@staff_member_required
def upload_policies(request):  # noqa: ANN001
    """Persiste CSV/XLSX; plantilla integrada en el sitio Admin (base_site)."""
    context = {
        **admin.site.each_context(request),
        "title": "Carga de pólizas (CSV / Excel)",
        "form": PolicyFileForm(),
        "error": None,
        "ingest_result": None,
        "result_json": None,
        "upload_type": "policies",
    }
    if request.method == "POST":
        form = PolicyFileForm(request.POST, request.FILES)
        context["form"] = form
        if form.is_valid():
            f = request.FILES["file"]
            content = f.read()
            try:
                result = ingest_policies_file(content, f.name, source="django")
                context.update(_result_payload(result))
            except Exception as e:
                context["error"] = str(e)
    return TemplateResponse(request, "admin/upload_policies.html", context)


@staff_member_required
def upload_claims(request):  # noqa: ANN001
    context = {
        **admin.site.each_context(request),
        "title": "Carga de siniestros (CSV / Excel)",
        "form": ClaimFileForm(),
        "error": None,
        "ingest_result": None,
        "result_json": None,
        "upload_type": "claims",
    }
    if request.method == "POST":
        form = ClaimFileForm(request.POST, request.FILES)
        context["form"] = form
        if form.is_valid():
            f = request.FILES["file"]
            content = f.read()
            try:
                result = ingest_claims_file(content, f.name, source="django")
                context.update(_result_payload(result))
            except Exception as e:
                context["error"] = str(e)
    return TemplateResponse(request, "admin/upload_claims.html", context)


@staff_member_required
def data_model(request):  # noqa: ANN001
    """Documentación del modelo lógico en PostgreSQL/Supabase (diagramas + tablas)."""
    context = {
        **admin.site.each_context(request),
        "title": "Modelo de datos y flujos",
    }
    return TemplateResponse(request, "admin/data_model.html", context)
