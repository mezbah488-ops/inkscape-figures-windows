#!/usr/bin/env python3
"""
watch_figures.py - monitors figures/ folder.
When any .svg is saved, exports it to .pdf + .pdf_tex via Inkscape.
This makes LaTeX equations typed in Inkscape text nodes render properly.

Usage:  python watch_figures.py <figures_folder>
"""
import sys, time, subprocess
from pathlib import Path
from shutil import which

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    sys.exit("[error] Run:  pip install watchdog")

INKSCAPE_OVERRIDE = ""
DEBOUNCE = 1.5

def find_inkscape():
    if INKSCAPE_OVERRIDE: return INKSCAPE_OVERRIDE
    for p in [r"C:\Program Files\Inkscape\bin\inkscape.exe",
              r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe"]:
        if Path(p).exists(): return p
    return which("inkscape") or ""

INKSCAPE = find_inkscape()

def export_svg(svg):
    if not INKSCAPE: print("[error] Inkscape not found."); return
    pdf = svg.with_suffix(".pdf")
    print(f"[export] {svg.name} -> .pdf + .pdf_tex")
    cmd = [INKSCAPE, str(svg), "--export-type=pdf",
           f"--export-filename={pdf}", "--export-latex"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            print(f"[ok]     {pdf.stem}.pdf  +  {pdf.stem}.pdf_tex")
        else:
            print(f"[fail]   code {r.returncode}")
            if r.stderr: print(r.stderr[:300])
    except subprocess.TimeoutExpired:
        print("[fail]   timed out")
    except Exception as e:
        print(f"[fail]   {e}")

class Handler(FileSystemEventHandler):
    def __init__(self): self._p = {}
    def on_modified(self, e):
        if not e.is_directory and Path(e.src_path).suffix.lower() == ".svg":
            self._p[e.src_path] = time.time()
    on_created = on_modified
    def flush(self):
        now = time.time()
        ready = [p for p,t in self._p.items() if now-t >= DEBOUNCE]
        for p in ready:
            del self._p[p]; export_svg(Path(p))

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    folder = Path(sys.argv[1]).resolve()
    if not folder.is_dir():
        sys.exit(f"[error] Not a directory: {folder}")
    h = Handler()
    obs = Observer()
    obs.schedule(h, str(folder), recursive=False)
    obs.start()
    print(f"[watch] Monitoring: {folder}")
    print("        Save any .svg -> auto-exports .pdf + .pdf_tex")
    print("        Press Ctrl-C to stop.\n")
    try:
        while True:
            time.sleep(0.3); h.flush()
    except KeyboardInterrupt:
        pass
    finally:
        obs.stop(); obs.join()
        print("\n[watch] Stopped.")

if __name__ == "__main__": main()
