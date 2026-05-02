"""
Genera el PDF de requerimientos BI a partir de:
  docs/pdf/requerimientos-infraestructura-bi-integral.html

Orden de preferencia:
  1) Chrome o Edge en modo headless (mismo motor que el navegador; layout fiel al HTML).
  2) xhtml2pdf (respaldo; algunos bloques se ven peor).

El logo se incrusta en base64 en una copia temporal para que el PDF no dependa de rutas
relativas al abrir file://.

Requisitos opcionales: pip install xhtml2pdf
"""
from __future__ import annotations

import base64
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "docs" / "pdf" / "requerimientos-infraestructura-bi-integral.html"
PDF_OUT = ROOT / "docs" / "pdf" / "infra-bi-la-fe.pdf"
LOGO = ROOT / "docs" / "pdf" / "assets" / "logo-seguros-la-fe.png"


def _embed_logo(html: str) -> str:
    if not LOGO.is_file():
        return html
    b64 = base64.b64encode(LOGO.read_bytes()).decode("ascii")
    return html.replace(
        'src="assets/logo-seguros-la-fe.png"',
        f'src="data:image/png;base64,{b64}"',
    )


def _find_chromium() -> str | None:
    env = os.environ.get("CHROME_PATH", "").strip()
    if env and Path(env).is_file():
        return env
    for candidate in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ):
        if Path(candidate).is_file():
            return candidate
    return None


def _pdf_via_headless_browser(html_file: Path, pdf_path: Path) -> bool:
    exe = _find_chromium()
    if not exe:
        return False
    uri = html_file.resolve().as_uri()
    pdf_path = pdf_path.resolve()
    try:
        subprocess.run(
            [
                exe,
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}",
                uri,
            ],
            check=True,
            timeout=120,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, OSError, FileNotFoundError) as e:
        print(f"[INFO] PDF vía navegador no disponible: {e}", file=sys.stderr)
        return False
    return pdf_path.is_file() and pdf_path.stat().st_size > 1500


def _pdf_via_xhtml2pdf(html: str, pdf_path: Path) -> bool:
    try:
        from xhtml2pdf import pisa
    except ImportError:
        print("Instale: pip install xhtml2pdf", file=sys.stderr)
        return False
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    base = str(HTML.parent.resolve()) + os.sep
    with pdf_path.open("wb") as out:
        status = pisa.CreatePDF(html, dest=out, encoding="utf-8", path=base)
    if getattr(status, "err", 0):
        print(f"[WARN] xhtml2pdf err={status.err}", file=sys.stderr)
    return pdf_path.is_file() and pdf_path.stat().st_size > 500


def main() -> None:
    if not HTML.is_file():
        print(f"No existe: {HTML}", file=sys.stderr)
        sys.exit(1)

    html = _embed_logo(HTML.read_text(encoding="utf-8"))

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".html",
        delete=False,
        encoding="utf-8",
        newline="\n",
    ) as tmp:
        tmp.write(html)
        tmp_path = Path(tmp.name)

    try:
        if _pdf_via_headless_browser(tmp_path, PDF_OUT):
            print(f"PDF generado (Chrome/Edge headless): {PDF_OUT}")
            return
    finally:
        tmp_path.unlink(missing_ok=True)

    print("[INFO] Usando xhtml2pdf como respaldo…", file=sys.stderr)
    if _pdf_via_xhtml2pdf(html, PDF_OUT):
        print(f"PDF generado (xhtml2pdf): {PDF_OUT}")
        return

    print("No se pudo generar el PDF.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
