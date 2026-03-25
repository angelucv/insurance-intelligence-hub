# Laboratorio (Streamlit)

Prototipos interactivos: curvas, persistencia, escenarios. En demos suele desplegarse en un entorno aislado (p. ej. Hugging Face Spaces).

## Arranque local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Secretos típicos: `COMPUTE_API_URL`, `DJANGO_ADMIN_BASE_URL`, opcional `PORTAL_REFLEX_URL` tras desplegar Reflex. Tema en `.streamlit/config.toml`. Carga de CSV solo en **Django Admin**. App de referencia: [insurance-suite.streamlit.app](https://insurance-suite.streamlit.app).
