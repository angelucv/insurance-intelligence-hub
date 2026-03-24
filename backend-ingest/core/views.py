"""Vistas internas: carga de maestros vía API de cómputo (validación centralizada)."""

from __future__ import annotations

import os

import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from core.forms import PolicyFileForm


@staff_member_required
def upload_policies(request):  # noqa: ANN001
    """Reenvía el archivo a FastAPI `/api/v1/ingest/policies` (misma validación Pydantic)."""
    context: dict = {"form": PolicyFileForm(), "result": None, "error": None}
    if request.method == "POST":
        form = PolicyFileForm(request.POST, request.FILES)
        context["form"] = form
        if form.is_valid():
            f = request.FILES["file"]
            base = os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000").rstrip("/")
            url = f"{base}/api/v1/ingest/policies"
            headers: dict[str, str] = {}
            key = os.environ.get("INGEST_API_KEY")
            if key:
                headers["X-API-Key"] = key
            try:
                r = requests.post(
                    url,
                    files={"file": (f.name, f.read(), getattr(f, "content_type", "application/octet-stream"))},
                    headers=headers,
                    timeout=120,
                )
                context["result"] = {"status_code": r.status_code, "text": r.text}
            except requests.RequestException as e:
                context["error"] = str(e)
    return render(request, "core/upload_policies.html", context)
