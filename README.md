[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/blackhan-software/xpower-banq-doc)
[![CI Main](https://github.com/blackhan-software/xpower-banq-doc/actions/workflows/ci-main.yml/badge.svg)](https://github.com/blackhan-software/xpower-banq-doc/actions/workflows/ci-main.yml)

# XPower Banq Docs

> Protocol documentation for XPower Banq; see [docs.xpowerbanq.com]!

[docs.xpowerbanq.com]: https://docs.xpowerbanq.com

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
bash paper/000.banq-all/banq-all.sh ## build whitepaper (requires pdflatex, pdfunite)
```

```sh
python -m paper.simulation.sim_debt all ## risk analysis (requires pip deps)
```

## Copyright

© 2025 [Moorhead LLC](#)
