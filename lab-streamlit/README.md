# Laboratorio (Streamlit)

Prototipos interactivos: curvas, persistencia, escenarios. En demos suele desplegarse en un entorno aislado (p. ej. Hugging Face Spaces).

## Arranque local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Secretos típicos: `COMPUTE_API_URL`, opcional `DJANGO_ADMIN_BASE_URL`, opcional `PORTAL_REFLEX_URL` (enlace al portal). Tema en `.streamlit/config.toml`. Carga de CSV solo en **Django Admin**.
