# Despliegue en tier gratuito (demo pública)

Objetivo: **URL de la API** (Render) + **URL del tablero** (Streamlit Community Cloud), sin coste para enseñar el flujo end-to-end.

## 1. API en Render

1. Cuenta en [Render](https://render.com).
2. **New** → **Blueprint** → conecta el repo de GitHub y selecciona `render.yaml`, o **Web Service** manual:
   - **Root Directory**: `backend-compute`
   - **Build**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance**: Free
3. Variable opcional: `CORS_ALLOW_ORIGINS` = `*` (ya va en el blueprint) o lista de orígenes separados por coma.
4. Copia la URL pública (p. ej. `https://insurance-hub-api.onrender.com`).

**Nota:** el plan gratuito **duerme** tras unos minutos sin tráfico; la primera petición puede tardar ~30–60 s en despertar. Para una demo en vivo, abre primero `/health` en el navegador o avisa a la audiencia.

Comprobación:

- `GET https://TU-URL/health`
- `GET https://TU-URL/api/v1/kpi/summary`

## 2. Tablero en Streamlit Community Cloud

1. Cuenta en [Streamlit Community Cloud](https://streamlit.io/cloud).
2. **New app** → repo → rama `main`.
3. **Main file path**: `lab-streamlit/app.py`
4. **Advanced settings** → **Python version** 3.11 (o la que use el app).
5. **Requirements file**: `lab-streamlit/requirements.txt`
6. **Secrets** (pegar):

```toml
COMPUTE_API_URL = "https://TU-URL-DE-RENDER.onrender.com"
```

7. Deploy. La app llamará a la API al cargar (tras el cold start de Render, puede fallar una vez; recargar suele bastar).

Referencia local: `lab-streamlit/.streamlit/secrets.toml.example`.

## 3. Alternativas gratuitas (opcional)

| Plataforma | Uso típico |
|------------|------------|
| [Railway](https://railway.app) | Crédito mensual limitado; API o todo-en-uno. |
| [Fly.io](https://fly.io) | Máquinas free tier; requiere CLI y algo más de setup. |
| [Hugging Face Spaces](https://huggingface.co/spaces) | Docker/SDK; buen plan B si quieres la API en un Space. |

## 4. Qué decir en una entrevista

- Excel y Power BI siguen siendo el día a día; este demo muestra **automatización y trazabilidad** (Pydantic + API + export CSV para PBI).
- Los datos son **sintéticos**; en producción se conectaría a la misma gobernanza que ya tengan (SQL, lake, etc.).
