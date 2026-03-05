# AGENTS.md

VitePress documentation site for the XPower Banq DeFi lending protocol. The VitePress site has no tests or linter; `worker/` has a `typecheck` step via `tsc --noEmit`.

## Commands

```sh
npm run dev              # Dev server at http://0.0.0.0:5174
npm run build            # Static site to .vitepress/dist/
npm run preview          # Preview built site
npm run ai-corpus        # Regenerate corpus from content/ (3 artifacts, see below)
npm run ai-worker:dev    # Cloudflare Worker locally (needs API key in env, see below)
npm run ai-worker:deploy # Deploy Worker
npm run ai-worker:install# Install worker/ dependencies (separate npm package)
npm run svg-widths       # Rewrite content/diagrams/*.svg to 588px width
```

`predev`/`prebuild` auto-run `svg-widths` + `ai-corpus` — no manual step for new SVGs.

## Adding a new page (easy to miss)

Requires **3 files**: the `.md` in `content/` + its sidebar entry in `.vitepress/config/sidebar.ts` + its navigation entry in `content/SUMMARY.md` (GitBook TOC). Skipping `SUMMARY.md` makes the page invisible on book.xpowerbanq.com.

## Key conventions

- `srcDir: 'content'` — all markdown lives under `content/`, not `docs/`
- `srcExclude: ['**/README.md', 'SUMMARY.md']` — these files are NOT VitePress pages
- **Math**: MathJax, `$...$` inline, `$$...$$` display
- **Custom containers**: `::: definition`, `::: theorem`, `::: proof`
- **SVGs**: referenced via **relative paths** (e.g. `../diagrams/foo.svg`) for VitePress + GitBook compatibility; auto dark-inverted via CSS `.dark img[src$=".svg"]`
- **Images**: same relative-path convention under `content/images/`
- **Logo SVGs** live under `content/public/logo/` (referenced as absolute `/logo/...`)
- **Add a new SVG** to `content/diagrams/`, then run `npm run build` (prebuild hook handles width normalization)
- **Build env vars**: `.env` (committed) for production defaults; `.env.local` (gitignored) for overrides. Only `VITE_`-prefixed vars reach client JS; unsetting `VITE_AI_WORKER_URL` disables the "Ask AI" widget entirely.

## Ask-AI / Corpus bundler

The `ai-corpus` script walks `content/` once and writes **3 artifacts**: `worker/source/ai-corpus.md` (Worker prompt), `content/public/llms.txt`, `content/public/llms-full.txt` (public AI crawler targets, gitignored). Skips `README.md`, `SUMMARY.md`, `index.md`, and `public/`. The bundler warns if the estimate exceeds 200K tokens. Full workflow in `.claude/skills/ai-corpus/SKILL.md`. `wrangler dev`/`deploy` also auto-regenerate the corpus via `wrangler.toml`'s `[build]` step (`--if-missing`).

## Cloudflare Worker (`worker/`)

- **Separate npm package** — install with `npm run ai-worker:install` (own `package-lock.json`, not covered by root install).
- **Local dev**: `npm run ai-worker:dev` forwards `$ANTHROPIC_API_KEY` or `$DEEPSEEK_API_KEY` (whichever is set) via `--var` to `wrangler dev`. The active provider and model are set in `worker/wrangler.toml` (currently `deepseek` / `deepseek-v4-flash`).
- **Typecheck** before deploy if modifying `worker/source/*.ts`: `npm --prefix worker run typecheck` (`tsc --noEmit`).
- **CI auto-deploy** on push to `main` when `worker/`, `content/`, or `scripts/ai-corpus/` change (requires `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` secrets).

## CI / Deploy flow

- **Push to `main`** → GH Pages deploy (site) + Worker deploy (if affected paths changed). No manual step.
- **Tags `v*`** → paper PDF release via `gh-paper.yml`.
- **PRs to `main`** → CI build check (site + paper if `paper/` touched).
- The main site build does NOT need `worker/` dependencies installed.

## LaTeX papers (paper/)

Canonical source, separate from the VitePress content. `paper/000.banq-all/banq-all.sh` builds all six papers + unified bundle (requires `pdflatex` + `latexmk`). CI builds paper PDFs in a `texlive/texlive` container on tags `v*` and PRs touching `paper/`.

## Simulation suite (paper/sims/)

```sh
pip install -r paper/sims/sim_debt/requirements.txt
python -m paper.sims.sim_debt all   # Full risk-analysis pipeline
```

Other sims under `paper/sims/`: `sim_caps`, `sim_equi`, `sim_game`, `sim_liqs`, `sim_twap`.
