# inkscape-figures-windows

A Windows-native workflow that connects **Neovim**, **Inkscape**, and **LaTeX** so you can create and edit vector figures without leaving your editor. Inspired by [Gilles Castel's](https://castel.dev/post/lecture-notes-2/) original Linux workflow — this is a full Windows port using Python and Batch scripts.

---

## How It Works

There are **two independent watchers** running in the background once you start working:

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

> **Note:** Both watchers run in separate terminal windows. They are started together by `fig start`.

---

## Prerequisites

Make sure the following are installed and available on your Windows **PATH**:

| Tool | Purpose | Download |
|------|---------|----------|
| Neovim | Editor | https://neovim.io |
| Inkscape 1.x | Drawing + PDF export | https://inkscape.org |
| Python 3 | Runs the watcher scripts | https://python.org |
| `py` launcher | Comes with Python installer | (bundled with Python) |
| MiKTeX or TeX Live | LaTeX compiler | https://miktex.org |

Verify everything is accessible from PowerShell:

```powershell
nvim --version
inkscape --version
python --version
py --version
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

### Step 2 — (Optional) Add `fig` to your PATH

To use `fig` as a command from any folder, add the repo directory to your system PATH:

1. Open **Start** → search **"Environment Variables"**
2. Under **User variables**, select **Path** → **Edit**
3. Click **New** and add: `C:\Users\YourName\inkscape-figures`
4. Click OK and restart PowerShell

Now you can run `fig` from any LaTeX project folder.

### Step 3 — Check Inkscape is detected

Both `inkscape_figures.py` and `watch_figures.py` have this line near the top:

```python
INKSCAPE_OVERRIDE = ""
```

If Inkscape is on your PATH, leave this empty — it will be found automatically. If not, set the full path manually in **both files**:

```python
INKSCAPE_OVERRIDE = r"C:\Program Files\Inkscape\bin\inkscape.exe"
```

---

## LaTeX Setup

### Step 4 — Add the `\incfig` command to your preamble

This tells LaTeX how to import the exported PDF figures. Add it once to each project's preamble:

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

## Neovim Setup

### Step 5 — Add the LuaSnip snippet

Add this to your LaTeX snippets file (e.g. `snippets/tex.json`). Typing `fig` and pressing **Tab** expands it into a complete figure block:

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

### Step 6 — Add the autocmd to `init.lua`

This starts both watchers automatically whenever you open a `.tex` file in Neovim.
Paste this at the bottom of your `init.lua`:

```lua
vim.api.nvim_create_autocmd("BufReadPost", {
  pattern = "*.tex",
  callback = function()
    local dir = vim.fn.expand("%:p:h")
    local fig_path = "C:\\Users\\YourName\\inkscape-figures\\fig.bat"

    -- Open a small terminal at the bottom of Neovim
    vim.cmd('split | term')
    vim.cmd('resize 5')

    -- cd into the .tex file's directory, init if needed, then start watchers
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

> **Important:** Replace `YourName` in `fig_path` with your actual Windows username,
> or use the full absolute path to wherever you cloned this repo.

What this does step by step:
- Runs `fig init` — creates the `figures/` folder and generates `start.bat` if they don't already exist
- Runs `fig start` — launches both watchers in separate terminal windows
- Returns your cursor to the editor immediately

---

## Daily Workflow

Once everything is set up, this is your day-to-day process:

1. **Open a `.tex` file** in Neovim — both watchers start automatically in the background
2. **Type** `fig` and press **Tab** — the figure snippet expands
3. **Fill in** a unique figure name, e.g. `free-body-diagram`
4. **Save** the file with `:w`
5. **Inkscape opens** automatically with a blank canvas (180×120mm template)
6. **Draw** your figure — you can use `$E=mc^2$` syntax in Inkscape text nodes for LaTeX equations
7. **Save** in Inkscape with `Ctrl+S` — after ~1.5 seconds, `.pdf` and `.pdf_tex` are generated in `figures/`
8. **Compile** your LaTeX document — the figure appears

---

## CLI Reference

You can also use `fig` directly from PowerShell inside any LaTeX project folder:

| Command | What it does |
|---------|-------------|
| `fig init` | Creates `figures/` folder and generates `start.bat` |
| `fig start` | Launches both watchers (calls `start.bat`) |
| `fig new <name>` | Creates a blank SVG and opens it in Inkscape immediately, without needing to save the `.tex` file first |
| `fig edit <name>` | Opens an existing figure in Inkscape |
| `fig list` | Lists all SVG figures in the current project |

Examples:

```powershell
cd C:\Users\YourName\my-paper
fig init
fig start
fig new circuit-diagram
fig edit circuit-diagram
fig list
```

---

## Project Structure

After running `fig init` and creating your first figure, your LaTeX project folder will look like this:

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
> Check the small terminal at the bottom of Neovim for Python errors. The most common cause is Inkscape not being on PATH. Set `INKSCAPE_OVERRIDE` in `inkscape_figures.py`.

**`.pdf` and `.pdf_tex` are not being generated after saving in Inkscape**
> Check the SVG-Exporter terminal window for error output. Make sure `watchdog` is installed (`pip install watchdog`) and that Inkscape is detected in `watch_figures.py`. Also check that `INKSCAPE_OVERRIDE` is set correctly if Inkscape is not on PATH.

**`fig` is not recognized as a command**
> Either add the repo folder to your PATH (see Step 2), or use the full path to the batch file: `C:\Users\YourName\inkscape-figures\fig.bat`.

**`fig start` says "Run fig init first"**
> You must run `fig init` once in each new LaTeX project folder before starting the watchers. It creates the `figures/` directory and the `start.bat` that `fig start` depends on.

**The watcher terminal in Neovim won't close**
> Click into it, press `i` to enter insert mode, type `exit`, and press Enter. Or from normal mode run `:bd!` to force-delete the buffer.

**LaTeX equations in Inkscape text nodes aren't rendering in the PDF**
> Make sure all four `\usepackage` lines and the `\incfig` command are in your preamble (see Step 4). Equation rendering is handled by the `.pdf_tex` file — check it was generated inside `figures/`.

**A new `\incfig{name}` was added but Inkscape didn't open**
> Watcher 1 only detects *new* figure names — names that weren't in the file the last time it was scanned. If you deleted and re-added the same name in the same session, it may not trigger. Use `fig new <name>` or `fig edit <name>` directly instead.

---

## Related

- [nvim-config-windows](https://github.com/mezbah488-ops/nvim-config-windows) — The Neovim config this workflow is built for
- [Gilles Castel's original post](https://castel.dev/post/lecture-notes-2/) — The Linux workflow this is based on
- [inkscape-figures (Linux)](https://github.com/gillescastel/inkscape-figures) — The original Python tool by Castel

---

## License

MIT
