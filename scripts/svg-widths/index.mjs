#!/usr/bin/env node
// Normalize every SVG under content/diagrams/ (recursive):
//
//   1. Set the root <svg> intrinsic width to TARGET_PX with proportional
//      height. The viewBox is left alone so visual content is unchanged.
//      GitBook clamps rendered images to the SVG's intrinsic size, so the
//      raw ~270px pt-based output from dvisvgm/pdf2svg renders too narrow
//      without this step.
//
//   2. Strip any internal <style> dark-mode block (legacy from a prior
//      design that double-inverted with the site CSS — see
//      .vitepress/theme/custom.css for the current single-source-of-truth
//      external rule tied to the .dark class).
//
// The theme-adaptive logo pair (BANQ-000.svg / BANQ-fff.svg) under
// content/public/logo/ is intentionally out of scope: VitePress serves
// the right one per theme, and injecting the prefers-color-scheme filter
// would double-invert the dark variant.
//
// Idempotent: re-running is a no-op once the SVGs are normalized.

import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { Normalizer } from './normalizer.js';
import { Svgs } from './svgs.js';

const ENV_ROOT_PATH = dirname(fileURLToPath(import.meta.url));
const ENV_REPO_PATH = join(ENV_ROOT_PATH, '..', '..');
const ENV_SVGS_PATH = join(ENV_REPO_PATH, 'content', 'diagrams');

const TARGET_PX = 588; // 0.8 × 735px GitBook content column

/**
 * Drive the normalization: discover every `.svg` under `ENV_SVGS_PATH`,
 * rewrite each root `<svg>`'s width/height to `TARGET_PX` with
 * proportional height, strip any legacy internal dark-style block,
 * and log a one-line summary.
 *
 * @returns {Promise<void>}
 */
async function main(tag = '[svg-widths]') {
  const svgs = new Svgs(ENV_SVGS_PATH, new Set());
  await svgs.io_read();
  const normalizer = new Normalizer(svgs.list, ENV_SVGS_PATH, TARGET_PX);
  await normalizer.io_normalize();
  normalizer.log_summary(tag);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  await main();
}
