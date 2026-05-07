#!/usr/bin/env node
// Bundle the docs into three artifacts from one Markdown walk:
//
//   worker/source/ai-corpus.md   — embedded in the Cloudflare Worker's
//                                  system prompt; powers the Ask-AI widget.
//   content/public/llms.txt      — public llmstxt.org index, served at
//                                  https://www.xpowerbanq.com/llms.txt
//   content/public/llms-full.txt — full Markdown bundle, served at
//                                  https://www.xpowerbanq.com/llms-full.txt
//
// Each `## FILE:` URL inside the bundles is the citable surface the
// AI tooling renders. Run `npm run ai-corpus` to regenerate all three;
// `predev`/`prebuild` hooks chain this automatically.
//
// The bundle targets ~93K tokens with comfortable headroom under
// Sonnet 4.6's 200K window.

import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { existsSync } from 'node:fs';

import { Blocks } from './blocks.js';
import { Corpus } from './corpus.js';
import { LlmsTxt } from './llms-txt.js';

const ENV_ROOT_PATH = dirname(fileURLToPath(import.meta.url));
const ENV_REPO_PATH = join(ENV_ROOT_PATH, '..', '..');
const ENV_TEXT_PATH = join(ENV_REPO_PATH, 'content');

const ENV_CORPUS_PATH = join(ENV_REPO_PATH, 'worker', 'source', 'ai-corpus.md');
const ENV_LLMS_INDEX_PATH = join(ENV_REPO_PATH, 'content', 'public', 'llms.txt');
const ENV_LLMS_FULL_PATH = join(ENV_REPO_PATH, 'content', 'public', 'llms-full.txt');

const ENV_SITE_URL = (process.env.BANQ_WWW_URL ?? 'https://www.xpowerbanq.com').replace(/\/+$/, '');

// README/SUMMARY/index are GitBook/VitePress nav scaffolding, not content.
const DOC_SKIP_BASE = new Set(['README.md', 'SUMMARY.md', 'index.md']);
const DOC_SKIP_DIRS = new Set(['public']);

/**
 * Orchestrate the build: read every page under `content/` once via
 * `Blocks`, then fan the result into both `Corpus` (worker bundle) and
 * `LlmsTxt` (public llmstxt.org index + full-corpus mirror). Honors
 * `--if-missing` by short-circuiting when *all three* outputs already
 * exist (used by wrangler's `[build]` step to break its watch loop).
 *
 * @returns {Promise<void>}
 */
async function main(tag = '[ai-corpus]') {
  const outs = [ENV_CORPUS_PATH, ENV_LLMS_INDEX_PATH, ENV_LLMS_FULL_PATH];
  if (skip_req(process.argv, outs)) {
    console.log(tag, 'all artifacts already exist');
    return;
  }
  const blocks = new Blocks(ENV_TEXT_PATH, DOC_SKIP_BASE, DOC_SKIP_DIRS);
  await blocks.io_read();

  const corpus = new Corpus(blocks.list, ENV_CORPUS_PATH, ENV_REPO_PATH);
  await corpus.io_write();
  corpus.log_summary(tag);

  const llms = new LlmsTxt(
    blocks.list, ENV_TEXT_PATH, ENV_LLMS_INDEX_PATH, ENV_LLMS_FULL_PATH, ENV_REPO_PATH, ENV_SITE_URL,
  );
  await llms.io_write();
  llms.log_summary(tag);
}

/**
 * Decide whether the build should short-circuit because `--if-missing`
 * was passed and *every* output is already present. Any single missing
 * artifact triggers a full regeneration so the three stay in sync.
 *
 * @param {string[]} argv The process argument vector to scan.
 * @param {string[]} dest_paths Absolute paths of the generated artifacts.
 * @returns {boolean} True iff the flag is set and all files are present.
 */
function skip_req(
  argv, dest_paths,
) {
  return argv.includes('--if-missing') && dest_paths.every((p) => existsSync(p));
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  await main();
}
