# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

XPower Banq protocol documentation site — a VitePress-based documentation for a permissionless DeFi lending protocol. This is a **documentation-only** repo (no application code). Content includes a whitepaper, mathematical appendices, simulation analyses, and reference material. Live site: [docs.xpowerbanq.com](https://docs.xpowerbanq.com).

## Commands

```bash
npm run dev       # Start dev server (host 0.0.0.0, port 5174)
npm run build     # Build static site to .vitepress/dist/
npm run preview   # Preview built site
```

No test suite or linter is configured. CI (`npm run build`) runs on push/PR to `main` via GitHub Actions (Node 22). A separate `gh-pages.yml` workflow deploys to GitHub Pages on push to `main`.

### LaTeX Paper Builds

Requires `pdflatex` and `pdfunite`. Run from project root:

```bash
bash paper/001.banq-pro/banq-pro.sh   # Build protocol whitepaper PDF
bash paper/002.banq-apx/banq-apx.sh   # Build appendices PDF
bash paper/003.banq-lck/banq-lck.sh   # Build lock paper PDF
bash paper/004.banq-log/banq-log.sh   # Build log-index paper PDF
bash paper/000.banq-all/banq-all.sh   # Build all + merge into banq-all.pdf
```

### Simulation Suite (Python)

The `paper/simulation/sim_debt/` package is a CLI for bad-debt risk analysis. Run from the repo root:

```bash
pip install -r paper/simulation/sim_debt/requirements.txt  # numpy, scipy, matplotlib, pandas, etc.

python -m paper.simulation.sim_debt oracle-lag     # Oracle lag model
python -m paper.simulation.sim_debt backtest       # Historical backtesting
python -m paper.simulation.sim_debt montecarlo     # Monte Carlo simulation (--quick for fast run)
python -m paper.simulation.sim_debt sensitivity    # Sensitivity analysis (requires MC results first)
python -m paper.simulation.sim_debt bound          # Analytical bound
python -m paper.simulation.sim_debt all            # Full pipeline
python -m paper.simulation.sim_debt validate       # Cross-validation tests (pytest)
```

Output goes to `paper/simulation/sim_debt/output/`. Additional standalone simulations: `sim_caps/`, `sim_equi/`, `sim_liqs/`, `sim_twap/` (each has independent `.py` scripts).

## Architecture

### VitePress Site

- **Config**: `.vitepress/config.ts` — sidebar, nav, custom `markdown-it-container` blocks, Vite server settings. Uses `srcDir: 'content'` so all markdown content lives in `content/`, not a `docs/` directory.
- **Theme**: `.vitepress/theme/` — extends default VitePress theme with `CustomHero.vue` (landing page hero) and `custom.css` (brand colors, figure/table styling, custom block styles)
- **Build output**: `.vitepress/dist/` — deployed to GitHub Pages
- **Content** (under `content/`):
  - `whitepaper/` — 10-chapter whitepaper (`01-introduction` through `10-conclusion`)
  - `appendices/` — three parts: math/proofs (A-C), simulations/risk (D-G), reference (glossary)
  - `reference/` — parameters, constants, glossary
  - `public/images/` — SVG figures (auto-inverted in dark mode via CSS filter)

### LaTeX Source (`paper/`)

Not part of the VitePress build. Contains the canonical source for the whitepaper and appendices:

- `001.banq-pro/banq-pro.tex` — protocol whitepaper
- `002.banq-apx/banq-apx.tex` — appendices
- `003.banq-lck/banq-lck.tex` — ring-buffer time locks
- `004.banq-log/banq-log.tex` — log-space compounding index
- `simulation/` — Python simulation code (6 sub-packages: `sim_caps`, `sim_debt`, `sim_equi`, `sim_game`, `sim_liqs`, `sim_twap`)
- `transaction/` — gas trace diffs for supply/borrow/settle/redeem operations
- `verification/` — formal verification notes (`formal-verification.md`)

## Key Details

- **Math rendering**: Built-in VitePress math support (`markdown.math: true`) using MathJax. Inline: `$...$`, display: `$$...$$`.
- **Custom containers**: Three `markdown-it-container` block types: `::: definition`, `::: theorem`, `::: proof`. Styled in `custom.css` using VitePress's info/tip/details block colors respectively.
- **Frontmatter**: Each whitepaper chapter has `title`, `prev`, and `next` fields for navigation.
- **Sidebar ↔ filesystem**: The sidebar in `config.ts` mirrors the directory layout — when adding new pages, update both the markdown file and the sidebar entries.
- **Canonical source**: `paper/*.tex` are the canonical documents. The `content/` markdown was adapted from these. Cross-references use VitePress-style links (e.g., `[Appendix B](/appendices/part-i-math/security-proofs)`).
- **SVG dark mode**: SVGs in `<figure>` elements are auto-inverted in dark mode via `filter: invert(1) hue-rotate(180deg)` in `custom.css`.
