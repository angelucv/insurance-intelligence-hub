"""Laboratorio mínimo: conectar después a backend-compute."""

import os

import requests
import streamlit as st

st.set_page_config(page_title="Lab — Insurance Intelligence Hub", layout="wide")
st.title("Laboratorio (demo base)")
st.caption("Configura COMPUTE_API_URL para enlazar la API de cómputo.")

base = os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000").rstrip("/")

if st.button("Probar /health"):
    try:
        r = requests.get(f"{base}/health", timeout=5)
        st.json(r.json())
    except Exception as e:
        st.error(f"No se pudo contactar la API: {e}")
