# Laboratorio (Streamlit)

Prototipos interactivos: curvas, persistencia, escenarios. En demos suele desplegarse en un entorno aislado (p. ej. Hugging Face Spaces).

## Arranque local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Configura `COMPUTE_API_URL` en entorno o `st.secrets`. La carga de CSV/XLSX es en **Django Admin** (`/admin/upload-policies/`); opcional: `DJANGO_ADMIN_BASE_URL` en secretos para enlazar.
