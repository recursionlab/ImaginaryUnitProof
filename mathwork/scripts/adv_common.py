from __future__ import annotations
import json, subprocess, tempfile, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NB = ROOT / "ImaginaryUnit.ipynb"

def load_nb():
    return json.loads(NB.read_text(encoding="utf-8"))

def cell_lines(idx: int):
    """Return list of (lineno, text) for code cell idx (1-based numbering within cell)."""
    nb = load_nb()
    src = "".join(nb["cells"][idx].get("source", []))
    return list(enumerate(src.splitlines(True), start=1))

def cell_source(idx: int) -> str:
    nb = load_nb()
    return "".join(nb["cells"][idx].get("source", []))

def cell_type(idx:int)->str:
    return load_nb()["cells"][idx]["cell_type"]

def run_py(code: str, timeout: int = 120) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir=str(ROOT)) as f:
        f.write(code); path = f.name
    try:
        out = subprocess.run(["python", path], cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return out.stdout + ("\nSTDERR:\n" + out.stderr if out.stderr.strip() else "")
    finally:
        os.remove(path)

OUTDIR = ROOT / "organized" / "audit_outputs" / "adversarial"
OUTDIR.mkdir(parents=True, exist_ok=True)
def write_round(n: int, content: str) -> Path:
    p = OUTDIR / f"Round_{n}.md"
    p.write_text(content, encoding="utf-8")
    return p
