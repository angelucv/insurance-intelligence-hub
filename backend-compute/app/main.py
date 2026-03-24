"""API mínima neutra: ampliar con routers y lógica actuarial."""

from fastapi import FastAPI

app = FastAPI(
    title="Insurance Intelligence Hub API",
    description="Capa de cómputo y endpoints (demo base).",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/info")
def info() -> dict[str, str]:
    return {
        "service": "backend-compute",
        "role": "api_and_analytics",
    }
