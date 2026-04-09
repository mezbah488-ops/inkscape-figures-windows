#!/usr/bin/env python3
"""
install.py  -  Run ONCE to set up the global Inkscape Figures workflow.
    python install.py
"""
import os, sys, shutil, subprocess, winreg
from pathlib import Path

HOME        = Path.home()
INSTALL_DIR = HOME / "inkscape-figures"
SRC         = Path(__file__).parent
MIKTEX_STY  = HOME / "AppData" / "Roaming" / "MiKTeX" / "tex" / "latex" / "local"

STY = r"""\ProvidesPackage{incfig}
\RequirePackage{import}
\RequirePackage{xifthen}
\RequirePackage{transparent}
\RequirePackage{pdfpages}
%  Usage: \incfig{name}  or  \incfig[0.8\columnwidth]{name}
\newcommand{\incfig}[2][\columnwidth]{%
    \def\svgwidth{#1}%
    \import{\figurepath/}{#2.pdf_tex}%
}
\providecommand{\figurepath}{figures}
"""

def banner(s): print(f"\n{'='*55}\n  {s}\n{'='*55}")
def ok(s):     print(f"  [ok]  {s}")
def warn(s):   print(f"  [!!]  {s}")

def step1_copy():
    banner("1/4  Copying scripts")
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    for f in ["inkscape_figures.py", "watch_figures.py", "fig.bat"]:
        src = SRC / f
        if src.exists():
            shutil.copy2(src, INSTALL_DIR / f); ok(f"Copied {f}")
        else:
            warn(f"Not found (skipping): {f}")

def step2_deps():
    banner("2/4  Installing Python packages")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog", "-q"])
    ok("watchdog ready")

def step3_sty():
    banner("3/4  Installing incfig.sty for MiKTeX")
    MIKTEX_STY.mkdir(parents=True, exist_ok=True)
    (MIKTEX_STY / "incfig.sty").write_text(STY, encoding="utf-8")
    ok(f"Written to {MIKTEX_STY / 'incfig.sty'}")
    for exe in ("miktex", "initexmf"):
        try:
            subprocess.run([exe, "--update-fndb"], check=True, capture_output=True)
            ok(f"MiKTeX FNDB refreshed"); break
        except Exception: continue
    else:
        warn("Could not auto-refresh. Open MiKTeX Console -> Tasks -> Refresh file name database.")

def step4_path():
    banner("4/4  Adding to PATH")
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment",
                              0, winreg.KEY_READ | winreg.KEY_WRITE)
        try: cur, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError: cur = ""
        entry = str(INSTALL_DIR)
        if entry.lower() in cur.lower():
            ok("Already in PATH")
        else:
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ,
                              cur.rstrip(";") + ";" + entry)
            ok(f"Added {entry}")
            print("  Open a NEW terminal for PATH change to take effect.")
        winreg.CloseKey(key)
    except Exception as e:
        warn(f"Could not write registry: {e}")
        warn(f"Add manually: {INSTALL_DIR}")

def done():
    print(f"""
{'='*55}
  Done! Here is how to use it:
{'='*55}

  For EVERY new LaTeX project (run once per project):
    1. Open terminal in your project folder
    2. Run:  fig init

  Then in your .tex preamble:
    \\usepackage{{incfig}}

  Start working:
    fig start          (or double-click start.bat)

  Type \\incfig{{name}} in your .tex and save.
  Inkscape opens. Draw. Write $equations$ in text nodes.
  Save in Inkscape (Ctrl-S). LaTeX compiles. Done.
{'='*55}
""")

if __name__ == "__main__":
    if sys.platform != "win32":
        sys.exit("Windows only.")
    step1_copy(); step2_deps(); step3_sty(); step4_path(); done()
