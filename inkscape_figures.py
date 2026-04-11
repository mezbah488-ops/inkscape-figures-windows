#!/usr/bin/env python3
import re, sys, time, subprocess
from pathlib import Path
from shutil import which

INKSCAPE_OVERRIDE = ""

def find_inkscape():
    if INKSCAPE_OVERRIDE:
        return INKSCAPE_OVERRIDE
    for p in [r"C:\Program Files\Inkscape\bin\inkscape.exe",
              r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe"]:
        if Path(p).exists():
            return p
    return which("inkscape") or ""

INKSCAPE = find_inkscape()

SVG = (
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        '<svg xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"\n'
        '     xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.0.dtd"\n'
        '     xmlns="http://www.w3.org/2000/svg"\n'
        '     width="180mm" height="120mm" viewBox="0 0 180 120" version="1.1"\n'
        '     inkscape:version="1.0">\n'
        '  <sodipodi:namedview inkscape:document-units="mm" units="mm"/>\n'
        '  <g inkscape:label="Figure" inkscape:groupmode="layer" id="layer1">\n'
        '    <!-- Draw here. LaTeX equations in text nodes: $E=mc^2$ -->\n'
        '  </g>\n'
        '</svg>\n'
)

RE = re.compile(r'\\incfig(?:\[.*?\])?\{([^}]+)\}')

def fdir(tex): return tex.parent / "figures"
def svg(tex, name): return fdir(tex) / (name + ".svg")

def open_ink(s):
    if not INKSCAPE:
        print("[error] Inkscape not found. Set INKSCAPE_OVERRIDE in inkscape_figures.py"); return
    print(f"[inkscape] Opening {s.name}")
    subprocess.Popen([INKSCAPE, str(s)])

def create(tex, name, open_after=True):
    fdir(tex).mkdir(exist_ok=True)
    s = svg(tex, name)
    if not s.exists():
        s.write_text(SVG, encoding="utf-8")
        print(f"[create] figures/{name}.svg")
    else:
        print(f"[exists] figures/{name}.svg")
    if open_after: open_ink(s)

def watch(tex):
    tex = tex.resolve()
    if not tex.exists(): sys.exit(f"[error] Not found: {tex}")
    print(f"[watch] {tex.name}  (Ctrl-C to stop)\n")
known = set(RE.findall(tex.read_text(encoding="utf-8", errors="ignore")))
mtime = tex.stat().st_mtime
time.sleep(2)  # wait for startup before monitoring
while True: 
    try:
        time.sleep(0.4)
            m = tex.stat().st_mtime
            if m == mtime: continue
            mtime = m
            cur = set(RE.findall(tex.read_text(encoding="utf-8", errors="ignore")))
            for n in sorted(cur - known):
                print(f"[detect] \\incfig{{{n}}}")
                create(tex, n)
            known = cur
            except KeyboardInterrupt:
            print("\n[watch] Stopped."); break

            def main():
        args = sys.argv[1:]
        if not args: sys.exit("Usage: inkscape_figures.py watch|create|edit <tex> [name]")
        cmd, *rest = args
        if cmd == "watch": watch(Path(rest[0]))
        elif cmd == "create": create(Path(rest[0]), rest[1])
    elif cmd == "edit":
        s = svg(Path(rest[0]), rest[1])
        if not s.exists(): sys.exit(f"[error] Not found: {s}")
        open_ink(s)
    else: sys.exit(f"Unknown: {cmd}")

    if __name__ == "__main__": main()
