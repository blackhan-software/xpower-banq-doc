[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/blackhan-software/xpower-banq-doc)
[![CI Main](https://github.com/blackhan-software/xpower-banq-doc/actions/workflows/ci-main.yml/badge.svg)](https://github.com/blackhan-software/xpower-banq-doc/actions/workflows/ci-main.yml)

# XPower Banq Docs

> Protocol documentation for XPower Banq; see [www.xpowerbanq.com]!

[www.xpowerbanq.com]: https://www.xpowerbanq.com

## Development

```sh
npm run dev ## npx vitepress dev docs
```

## Build

```sh
npm run build ## npx vitepress build docs
```

## Preview

```sh
npm run preview ## npx vitepress preview docs
```

## Paper

LaTeX source and Python simulations live in `paper/`:

```sh
bash paper/000.banq-all/banq-all.sh ## build whitepaper (requires pdflatex, latexmk)
```

```sh
python -m paper.sims.sim_debt all ## risk analysis (requires pip deps)
```

## Copyright

© 2025 [Moorhead LLC](#)
