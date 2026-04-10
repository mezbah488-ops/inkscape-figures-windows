# inkscape-figures-windows

A Windows-native workflow that connects **Neovim**, **Inkscape**, and **LaTeX** so you can create and edit vector figures without leaving your editor. Inspired by [Gilles Castel's](https://castel.dev/post/lecture-notes-2/) original Linux workflow — this is a full Windows port using Python and Batch scripts.

---

## How It Works

There are **two independent watchers** running silently in the background once you open a `.tex` file:

```
┌─────────────────────────────────────────────────────────────────┐
│  Watcher 1: inkscape_figures.py watch                           │
│                                                                 │
│  Monitors your .tex file every 0.4s                             │
│  When a new \incfig{name} is detected after a save:             │
│    → Creates figures/name.svg (blank template)                  │
│    → Opens Inkscape with that file                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Watcher 2: watch_figures.py                                    │
│                                                                 │
│  Monitors the figures/ folder using watchdog                    │
│  When any .svg is saved in Inkscape:                            │
│    → Runs Inkscape CLI to export .pdf + .pdf_tex                │
│    → Your LaTeX compiler picks these up automatically           │
└─────────────────────────────────────────────────────────────────┘
```

So the full loop looks like this:

```
You type \incfig{name} in Neovim and save
    → Watcher 1 detects the new figure name in the .tex file
    → figures/name.svg is created from a blank template
    → Inkscape opens automatically with that file

You draw your figure and save in Inkscape (Ctrl+S)
    → Watcher 2 detects the .svg change (after a 1.5s debounce)
    → Inkscape CLI exports figures/name.pdf + figures/name.pdf_tex

You compile LaTeX
    → \incfig{name} renders your figure in the document
```

Both watchers are started automatically in the background by the
[inkscape-figures.nvim](https://github.com/mezbah488-ops/inkscape-figures.nvim)
plugin when you open any `.tex` file in Neovim. No terminal windows, no manual
setup per project.

---

## Prerequisites

Make sure the following are installed and available on your Windows **PATH**:

| Tool | Purpose | Download |
|------|---------|----------|
| Neovim | Editor | https://neovim.io |
| Inkscape 1.x | Drawing + PDF export | https://inkscape.org |
| Python 3 | Runs the watcher scripts | https://python.org |
| MiKTeX or TeX Live | LaTeX compiler | https://miktex.org |

Verify everything is accessible from PowerShell:

```powershell
nvim --version
inkscape --version
python --version
```

Install the one required Python dependency:

```powershell
pip install watchdog
```

---

## Installation

### Step 1 — Clone this repo to a permanent location

```powershell
git clone https://github.com/mezbah488-ops/inkscape-figures-windows.git C:\Users\YourName\inkscape-figures
```

Your folder should contain:

```
inkscape-figures/
├── fig.bat                 # Entry point — the main command you run
├── inkscape_figures.py     # Watcher 1: monitors .tex, opens Inkscape
├── watch_figures.py        # Watcher 2: monitors figures/, exports SVG→PDF
└── install.py              # One-time setup helper
```

### Step 2 — Run the installer

```powershell
cd C:\Users\YourName\inkscape-figures
python install.py
```

This will:
- Install the `watchdog` Python package
- Install `incfig.sty` into MiKTeX's local texmf tree
- Add the folder to your user PATH so `fig` works from anywhere

### Step 3 — Install the Neovim plugin

Add this to your [lazy.nvim](https://github.com/folke/lazy.nvim) plugin list:

```lua
{
  "mezbah488-ops/inkscape-figures.nvim",
  ft = "tex",
  opts = {},
}
```

Then open Neovim and run `:Lazy sync`.

That's it. No changes to `init.lua` beyond that one plugin entry. The plugin
handles everything — starting the watchers silently when you open a `.tex` file,
and opening figures in Inkscape from the editor.

---

## LaTeX Setup

### Step 4 — Add `\incfig` to your preamble

```latex
\usepackage{incfig}
```

`incfig.sty` was installed globally by `install.py`, so this single line is all
you need in every project.

Optionally set a custom figures path (default is `figures/`):

```latex
\renewcommand{\figurepath}{my-figures}
```

---

## Daily Workflow

1. **Open a `.tex` file** in Neovim — both watchers start silently in the background
2. **Type** `\incfig{my-diagram}` anywhere in your document and **save**
3. **Inkscape opens** automatically with a blank 180×120mm canvas
4. **Draw** your figure — type `$E=mc^2$` in text nodes for LaTeX equations
5. **Save** in Inkscape with `Ctrl+S` — `.pdf` and `.pdf_tex` are generated automatically
6. **Compile** your LaTeX document — the figure appears with properly rendered equations
7. **To edit** an existing figure — place cursor on `\incfig{name}` and press `<leader>fe`

---

## CLI Reference

You can also use `fig` directly from PowerShell inside any LaTeX project folder:

| Command | What it does |
|---------|-------------|
| `fig init` | Creates `figures/` folder and generates `start.bat` |
| `fig start` | Launches both watchers in the background |
| `fig new <name>` | Creates a blank SVG and opens it in Inkscape immediately |
| `fig edit <name>` | Opens an existing figure in Inkscape |
| `fig list` | Lists all SVG figures in the current project |

---

## Project Structure

After running `fig init` and creating your first figure:

```
my-paper/
├── main.tex
├── start.bat                         # Auto-generated by fig init
└── figures/
    ├── free-body-diagram.svg         # Source file — edit this in Inkscape
    ├── free-body-diagram.pdf         # Auto-generated on Inkscape save
    └── free-body-diagram.pdf_tex     # Auto-generated on Inkscape save
```

> Only `.svg` files need to be committed to version control.
> The `.pdf` and `.pdf_tex` files are regenerated automatically every time you save in Inkscape.

---

## Troubleshooting

**Inkscape doesn't open after saving the `.tex` file**
> The most common cause is Inkscape not being on PATH. Set `INKSCAPE_OVERRIDE` in `inkscape_figures.py`.

**`.pdf` and `.pdf_tex` are not generated after saving in Inkscape**
> Make sure `watchdog` is installed (`pip install watchdog`) and that Inkscape is detected in `watch_figures.py`.

**`fig` is not recognized as a command**
> Either re-run `install.py`, or add the repo folder to your PATH manually.

**`fig start` says "Run fig init first"**
> Run `fig init` once in each new LaTeX project folder before starting the watchers.

**A new `\incfig{name}` was added but Inkscape didn't open**
> Watcher 1 only detects *new* figure names per session. Use `fig new <name>` or `fig edit <name>` directly instead.

**LaTeX equations in Inkscape text nodes aren't rendering**
> Make sure `\usepackage{incfig}` is in your preamble and that `.pdf_tex` was generated in `figures/`.

---

## Related

- [inkscape-figures.nvim](https://github.com/mezbah488-ops/inkscape-figures.nvim) — The Neovim plugin that ties everything together
- [nvim-config-windows](https://github.com/mezbah488-ops/nvim-config-windows) — The Neovim config this workflow is built for
- [Gilles Castel's original post](https://castel.dev/post/lecture-notes-2/) — The Linux workflow this is based on
- [inkscape-figures (Linux)](https://github.com/gillescastel/inkscape-figures) — The original Python tool by Castel
