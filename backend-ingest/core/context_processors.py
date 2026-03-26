"""Contexto global de plantillas (enlaces a portales sin repetir en cada vista)."""

from django.conf import settings


def portal_links(_request):
    return {
        "reflex_portal_url": getattr(settings, "REFLEX_PORTAL_URL", ""),
        "streamlit_lab_url": getattr(settings, "STREAMLIT_LAB_URL", ""),
        "compute_api_public_hint": getattr(settings, "COMPUTE_API_PUBLIC_HINT", ""),
    }
