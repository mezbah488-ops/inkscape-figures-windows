# Inkscape Figures — Windows Automation for Neovim + LaTeX

A Windows-native workflow that connects **Neovim**, **Inkscape**, and **LaTeX** so you can create, edit, and embed vector figures without ever leaving your editor.

Inspired by [Gilles Castel's](https://castel.dev/post/lecture-notes-2/) original Linux workflow, this is a full port for Windows using Python and Windows Batch files.

---

## How It Works

```
You type "fig" in Neovim  →  Tab expands a LaTeX figure block
You save the .tex file     →  Watcher detects the new figure name
                           →  Inkscape opens automatically
You draw and save (Ctrl+S) →  PDF is generated in figures/
You compile LaTeX          →  Your figure appears in the document
```

Everything happens automatically after the initial setup.

---

## Prerequisites

Before starting, make sure the following are installed and added to your Windows **PATH**:

| Tool | Purpose | Download |
|------|---------|----------|
| Neovim | Editor | https://neovim.io |
| Inkscape | Vector drawing | https://inkscape.org |
| Python 3 | Runs the watcher scripts | https://python.org |
| MiKTeX or TeX Live | LaTeX compiler | https://miktex.org |

To verify everything is on PATH, run these in PowerShell:

```powershell
nvim --version
inkscape --version
python --version
```

---

## Installation

### Step 1 — Clone this repo

```powershell
git clone https://github.com/mezbah488-ops/inkscape-figures-windows.git C:\Users\YourName\inkscape-figures
```

Your script directory should look like this:

```
inkscape-figures/
├── fig.bat                 # Entry point — run this from Neovim
├── inkscape_figures.py     # Core figure management logic
├── watch_figures.py        # File watcher — detects new figure names
└── install.py              # One-time setup helper
```

### Step 2 — Run the installer

```powershell
cd C:\Users\YourName\inkscape-figures
python install.py
```

This sets up any dependencies and verifies your environment.

---

## Neovim Setup

### Step 3 — Add the LaTeX snippet

Add the following to your LaTeX snippets file (e.g. `snippets/tex.json`). This gives you a `fig` trigger that expands into a complete figure block:

```json
"Inkscape Figure": {
    "prefix": "fig",
    "body": [
        "\\begin{figure}[ht]",
        "\t\\centering",
        "\t\\incfig[0.8\\columnwidth]{${1:figure_name}}",
        "\t\\caption{${2:Your caption here}}",
        "\\end{figure}"
    ],
    "description": "Insert Inkscape figure with 0.8 columnwidth"
}
```

### Step 4 — Add the watcher autocmd to `init.lua`

Paste this at the bottom of your `init.lua`. It automatically starts the figure watcher whenever you open a `.tex` file:

```lua
vim.api.nvim_create_autocmd("BufReadPost", {
  pattern = "*.tex",
  callback = function()
    local dir = vim.fn.expand("%:p:h")
    local fig_path = "C:\\Users\\YourName\\inkscape-figures\\fig.bat"

    -- Open a small terminal at the bottom of the screen
    vim.cmd('split | term')
    vim.cmd('resize 5')

    -- Initialize the figures/ folder if needed, then start watching
    local cmd = string.format(
      "cd /d %s && call \"%s\" init && call \"%s\" start\13",
      vim.fn.shellescape(dir),
      fig_path,
      fig_path
    )

    vim.fn.chansend(vim.b.terminal_job_id, cmd)
    vim.cmd('wincmd k') -- Return focus to the editor
  end
})
```

> **Important:** Replace `YourName` in `fig_path` with your actual Windows username.

### Step 5 — Add `\incfig` to your LaTeX preamble

This command tells LaTeX how to find and render the generated PDFs:

```latex
\usepackage{import}
\usepackage{xifthen}
\usepackage{pdfpages}
\usepackage{transparent}

\newcommand{\incfig}[2][1]{%
    \def\svgwidth{#1\columnwidth}
    \import{./figures/}{#2.pdf_tex}
}
```

---

## Daily Workflow

Once configured, this is all you do:

1. **Open your `.tex` file** in Neovim — a small watcher terminal appears briefly at the bottom
2. **Type** `fig` and press **Tab** — a figure block is inserted
3. **Fill in** a unique figure name, e.g. `force-diagram`
4. **Save** with `:w` — the watcher detects the new name
5. **Draw** in the Inkscape window that automatically opens
6. **Save** in Inkscape with `Ctrl+S` — a PDF is generated in `figures/`
7. **Compile** your LaTeX document — the figure appears automatically

---

## Project Structure (in your LaTeX folder)

After running `fig init`, your project will look like this:

```
my-paper/
├── main.tex
└── figures/
    ├── force-diagram.svg       # Source file — edit this in Inkscape
    ├── force-diagram.pdf       # Auto-generated on Inkscape save
    └── force-diagram.pdf_tex   # Auto-generated — do not edit
```

Only the `.svg` files need to be committed to version control. The `.pdf` and `.pdf_tex` files are generated automatically.

---

## Troubleshooting

**`fig` is not recognized as a command**
> Check that the `fig_path` in your `init.lua` exactly matches where `fig.bat` is located on your machine.

**Inkscape doesn't open**
> Look at the small terminal window at the bottom of Neovim — it will show any Python errors or path issues.

**The watcher terminal won't close**
> Click into the terminal, press `i` to enter insert mode, type `exit`, then press Enter. Or run `:bd!` from normal mode to force-close it.

**PDF not updating after saving in Inkscape**
> Make sure Inkscape is fully installed and on your PATH. Run `inkscape --version` in PowerShell to confirm.

**Figure doesn't appear after LaTeX compilation**
> Check that the `\incfig` command is in your preamble and that the figure name in your `.tex` file exactly matches the `.svg` filename in `figures/`.

---

## Related

- [nvim-config-windows](https://github.com/mezbah488-ops/nvim-config-windows) — The Neovim config this workflow is built for
- [Gilles Castel's original post](https://castel.dev/post/lecture-notes-2/) — The Linux workflow this is based on
- [inkscape-figures (Linux)](https://github.com/gillescastel/inkscape-figures) — The original Python tool

---

## License

MIT
