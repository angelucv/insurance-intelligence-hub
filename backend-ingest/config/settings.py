"""
Django — ingestión y admin (Insurance Intelligence Hub).
"""

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-in-production")
DEBUG = os.environ.get("DEBUG", "true").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

# HTTPS detrás del proxy (Render): sin esto Django cree que la petición es HTTP y falla la verificación CSRF.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Orígenes permitidos para POST con cookie CSRF (Django 4+). Render suele definir RENDER_EXTERNAL_URL.
CSRF_TRUSTED_ORIGINS: list[str] = []
for _chunk in (
    os.environ.get("RENDER_EXTERNAL_URL", ""),
    os.environ.get("CSRF_TRUSTED_ORIGINS", ""),
):
    for _part in _chunk.split(","):
        _u = _part.strip().rstrip("/")
        if _u and _u not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(_u)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Primero: sobrescribe plantillas del admin empaquetado (p. ej. admin/index.html).
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.portal_links",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

_default_sqlite = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
_db_url = os.environ.get("DATABASE_URL", _default_sqlite)
DATABASES = {
    "default": dj_database_url.config(
        default=_db_url,
        conn_max_age=600,
    )
}
# Supabase / Postgres en la nube suele exigir TLS; sin esto pueden fallar sesiones y vistas autenticadas (500).
if DATABASES["default"].get("ENGINE") == "django.db.backends.postgresql":
    opts = DATABASES["default"].setdefault("OPTIONS", {})
    if "sslmode=" not in _db_url.lower():
        opts.setdefault("sslmode", "require")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-ve"
TIME_ZONE = "America/Caracas"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Marca La Fe y activos compartidos del monorepo (collectstatic en Render incluye ../static/brand).
_REPO_STATIC = BASE_DIR.parent / "static"
STATICFILES_DIRS = [_REPO_STATIC] if _REPO_STATIC.is_dir() else []
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Enlaces mostrados en el admin (sidebar / ayuda). Sobreescribibles por entorno en despliegue.
REFLEX_PORTAL_URL = os.environ.get("REFLEX_PORTAL_URL", "https://insurance-suite.reflex.run").strip()
STREAMLIT_LAB_URL = os.environ.get("STREAMLIT_LAB_URL", "").strip()
# Texto opcional para documentación (p. ej. URL pública de la API de cómputo, sin secretos).
COMPUTE_API_PUBLIC_HINT = os.environ.get("COMPUTE_API_PUBLIC_HINT", "").strip()
