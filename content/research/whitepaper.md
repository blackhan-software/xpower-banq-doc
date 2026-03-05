# Whitepaper

The full XPower Banq whitepaper is published as a six-paper bundle — five individually published preprints plus a companion reference. It covers the protocol design, two engineering primitives, formal theory, empirical evaluation, and a full reference (bibliography + glossary).

## The bundle

- **[Protocol](/research/papers/protocol)** — the user-facing protocol mechanics in academic detail.
- **[Ring-buffer locks](/research/papers/ring-buffer-locks)** — the 16-slot quarterly time-lock primitive.
- **[Log-space index](/research/papers/log-space-index)** — the log-space cumulative interest accumulator.
- **[Theory and proofs](/research/papers/theory-and-proofs)** — formal proofs (cascade attenuation, Sybil rate-limiting, governance bounds, Nash equilibrium).
- **[Simulations](/research/papers/simulations)** — empirical validation across capacity dynamics, cascade dynamics, TWAP manipulation, and Merton jump-diffusion bad-debt analysis.
- **Reference (`banq-ref`)** — consolidated bibliography and glossary. Bundled into `banq-all.pdf` but not arXiv-published as a standalone preprint.

## Where to find the PDF

The PDFs are published as tagged GitHub releases:

- **[banq-all.pdf](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-all.pdf)** — the full unified bundle (all six papers, single PDF, single TOC, single bibliography).
- Individual PDFs (`banq-pro`, `banq-lck`, `banq-log`, `banq-mtp`, `banq-sim`, `banq-ref`) are linked from the [companion-paper landing pages](/research/papers/protocol).
- Browse all releases: [github.com/blackhan-software/xpower-banq-doc/releases](https://github.com/blackhan-software/xpower-banq-doc/releases).

## Citing the work

```
@misc{xpower-banq-2026,
  title  = {XPower Banq: A Permissionless DeFi Lending Protocol},
  author = {The Ri₺ch, Kârūn},
  year   = {2026},
  url    = {https://github.com/blackhan-software/xpower-banq-doc}
}
```
