# Laboratorio (Streamlit)

Prototipos interactivos: curvas, persistencia, escenarios. En demos suele desplegarse en un entorno aislado (p. ej. Hugging Face Spaces).

## Arranque local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Configura la URL de la API en variables de entorno o en `st.secrets` para no hardcodear entornos.
