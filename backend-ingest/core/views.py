"""Vistas internas: carga de maestros vía API de cómputo (validación centralizada)."""

from __future__ import annotations

import os
import time

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
            content = f.read()
            mime = getattr(f, "content_type", "application/octet-stream")
            try:
                # Despierta la API (tier gratuito Render) antes de un POST grande.
                try:
                    requests.get(f"{base}/health", timeout=45)
                except requests.RequestException:
                    pass
                r = None
                for attempt in range(5):
                    r = requests.post(
                        url,
                        files={"file": (f.name, content, mime)},
                        headers=headers,
                        timeout=120,
                    )
                    if r.status_code != 429:
                        break
                    if attempt < 4:
                        time.sleep(10 + attempt * 5)
                if r is None:
                    context["error"] = "Sin respuesta del servidor de ingestión."
                else:
                    context["result"] = {"status_code": r.status_code, "text": r.text}
            except requests.RequestException as e:
                context["error"] = str(e)
    return render(request, "core/upload_policies.html", context)
