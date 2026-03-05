---
name: ai-corpus
description: Rebuild the Ask-AI Cloudflare Worker corpus (worker/source/ai-corpus.md) from content/. Verifies the result fits under Sonnet 4.6's 200K context window.
allowed-tools: Bash Read Edit
---

# Rebuild Ask-AI Corpus

Regenerate `worker/source/ai-corpus.md` — the documentation bundle the Ask-AI side-panel widget reads as its system prompt. The bundler walks `content/**/*.md`, strips frontmatter, prepends one `## FILE: /url/path` header per page, and concatenates them with `---` separators.

## When to run manually

`wrangler dev` and `wrangler deploy` re-run the bundler automatically via `worker/wrangler.toml`'s `[build]` step (with `--if-missing` for the watch loop). Manual runs are only needed when verifying size locally before pushing, or after deleting `worker/source/ai-corpus.md` to force a fresh build.

## Steps

### 1. Run the bundler

```bash
npm run ai-corpus
```

Expected output:

```
ai-corpus: worker/source/ai-corpus.md <KiB> KiB (~<N> tokens), <count> files
```

Typical size is less than 100K tokens, leaving roughly half the budget unused under Sonnet 4.6's 200K standard input window. The script warns if the estimate exceeds 200K.

### 2. Spot-check the output

```bash
grep -c "^## FILE:" worker/source/ai-corpus.md
```

Should match the `<count>` the bundler logged. No `## SOURCE:`, `## CODE:`, or `## CLI:` markers should appear — the corpus is single-tier.

### 3. If over budget

Overflow is unlikely at current size but possible if `content/` grows substantially. The mitigation is to either shorten the offending pages, split a long page across two URLs, or add a basename to `DOC_SKIP_BASE` in `scripts/ai-corpus/index.mjs` if a page is genuinely non-citable nav scaffolding. Never silently truncate; the worker runs without the `context-1m` beta and Anthropic will reject overflowing requests.
