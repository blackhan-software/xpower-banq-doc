import { readFile, writeFile } from 'node:fs/promises';
import { relative } from 'node:path';

// Legacy internal dark-style block (with optional surrounding whitespace).
// We strip it on every run; injection is no longer performed.
const LEGACY_DARK_STYLE_RE = /\s*<style>@media \(prefers-color-scheme: dark\)\{svg\{filter:invert\(1\) hue-rotate\(180deg\)\}\}<\/style>/g;

const SVG_TAG_RE = /<svg\b[^>]*>/;
const ATTR_RE = (name) => new RegExp(`\\s${name}="([^"]*)"`);
const NUM_RE = /^([\d.]+)\s*([a-z%]*)$/i;

/**
 * Per-file SVG normalization driver and stat collector. Construction
 * stores the file list and tunables; `io_normalize()` reads each file,
 * applies the root-`<svg>` width rewrite and the legacy dark-style
 * strip, writes back when content changed, and accumulates counters;
 * `log_summary()` prints a one-line summary plus any failure warnings.
 */
export class Normalizer {
  /**
   * @param {string[]} files Absolute paths of `.svg` files to process.
   * @param {string} root_path Absolute root, used to render relative labels.
   * @param {number} target_px Intrinsic width to set on every root <svg>.
   */
  constructor(
    files, root_path, target_px,
  ) {
    this.files = files;
    this.root_path = root_path;
    this.target_px = target_px;
    this.width_rewrites = 0;
    this.dark_strips = 0;
    this.unchanged = 0;
    /** @type {string[]} Per-file failure messages (`label: status`). */
    this.failures = [];
  }

  /**
   * Read every file in `files`, apply the root-`<svg>` width rewrite
   * and the legacy dark-style strip, write back when content changed,
   * and update counters. Logs a one-line entry per file actually
   * rewritten so a tail of stdout shows what the run did.
   *
   * @returns {Promise<void>}
   */
  async io_normalize() {
    for (const path of this.files) {
      const label = relative(this.root_path, path);
      const original = await readFile(path, 'utf8');
      let svg = original;
      const changes = [];

      const width_result = rewrite_root(svg, this.target_px);
      if (width_result.status === 'rewritten') {
        svg = width_result.svg;
        changes.push(`width ${width_result.from} -> ${width_result.to}`);
        this.width_rewrites++;
      } else if (width_result.status !== 'already-normalized') {
        this.failures.push(`${label}: ${width_result.status}`);
      }

      const dark_result = strip_legacy_dark_style(svg);
      if (dark_result.changed) {
        svg = dark_result.svg;
        changes.push('- legacy dark <style>');
        this.dark_strips++;
      }

      if (svg !== original) {
        await writeFile(path, svg);
        console.log(`  ${label}: ${changes.join(', ')}`);
      } else {
        this.unchanged++;
      }
    }
  }

  /**
   * Log a one-line summary of what changed (or didn't), followed by
   * `WARN` lines for any failures collected during normalization.
   *
   * @param {string} tag Leading log tag identifying this run (e.g. `[svg-widths]`).
   * @returns {void}
   */
  log_summary(tag) {
    console.log(
      tag, `${this.width_rewrites} width rewrites, ${this.dark_strips} legacy-dark-style strips, ${this.unchanged} unchanged, ${this.failures.length} skipped`,
    );
    for (const f of this.failures) console.log(tag, `WARN ${f}`);
  }
}

/**
 * Parse an SVG length attribute (e.g. `"100"`, `"768.0px"`, `"50%"`)
 * into a numeric value plus a unit. Returns `null` if the value is not
 * a recognizable number-with-unit. The default unit is `"px"`.
 *
 * @param {string} value Raw attribute value.
 * @returns {{ value: number, unit: string } | null}
 */
function parse_length(value) {
  const m = NUM_RE.exec(value.trim());
  if (!m) return null;
  return { value: parseFloat(m[1]), unit: (m[2] || 'px').toLowerCase() };
}

/**
 * Rewrite the root `<svg>` tag's `width`/`height` to `target_px` (with
 * proportional height) without touching `viewBox`. Falls back to the
 * `viewBox` for missing/non-numeric width/height. Returns the new svg
 * along with a status string and (for successful rewrites) the
 * from/to dimension labels used in the per-file log line.
 *
 * Statuses: `rewritten`, `already-normalized`, `no-svg-tag`, `no-dimensions`.
 *
 * @param {string} svg Raw SVG source.
 * @param {number} target_px Intrinsic width to set on the root element.
 * @returns {{ svg: string, status: string, from?: string, to?: string }}
 */
function rewrite_root(svg, target_px) {
  const tag_match = SVG_TAG_RE.exec(svg);
  if (!tag_match) return { svg, status: 'no-svg-tag' };
  const tag = tag_match[0];

  const width_match = ATTR_RE('width').exec(tag);
  const height_match = ATTR_RE('height').exec(tag);
  const view_box_match = ATTR_RE('viewBox').exec(tag);

  let intrinsic_w = width_match ? parse_length(width_match[1]) : null;
  let intrinsic_h = height_match ? parse_length(height_match[1]) : null;

  // If width/height are missing or non-numeric (e.g. "100%"), fall back to viewBox.
  if ((!intrinsic_w || !intrinsic_h) && view_box_match) {
    const parts = view_box_match[1].trim().split(/[\s,]+/).map(Number);
    if (parts.length === 4 && parts.every(Number.isFinite)) {
      intrinsic_w = intrinsic_w ?? { value: parts[2], unit: 'px' };
      intrinsic_h = intrinsic_h ?? { value: parts[3], unit: 'px' };
    }
  }

  if (!intrinsic_w || !intrinsic_h || intrinsic_w.value <= 0 || intrinsic_h.value <= 0) {
    return { svg, status: 'no-dimensions' };
  }

  const aspect = intrinsic_h.value / intrinsic_w.value;
  const new_w = target_px;
  const new_h = Math.round(new_w * aspect * 1000) / 1000;
  const new_w_attr = `width="${fmt_length(new_w)}px"`;
  const new_h_attr = `height="${fmt_length(new_h)}px"`;

  if (
    intrinsic_w.unit === 'px' && Math.abs(intrinsic_w.value - new_w) < 0.001 &&
    intrinsic_h.unit === 'px' && Math.abs(intrinsic_h.value - new_h) < 0.001
  ) {
    return { svg, status: 'already-normalized' };
  }

  let new_tag = tag;
  new_tag = width_match
    ? new_tag.replace(ATTR_RE('width'), ` ${new_w_attr}`)
    : new_tag.replace('<svg', `<svg ${new_w_attr}`);
  new_tag = height_match
    ? new_tag.replace(ATTR_RE('height'), ` ${new_h_attr}`)
    : new_tag.replace('<svg', `<svg ${new_h_attr}`);

  return {
    svg: svg.slice(0, tag_match.index) + new_tag + svg.slice(tag_match.index + tag.length),
    status: 'rewritten',
    from: `${intrinsic_w.value}${intrinsic_w.unit}x${intrinsic_h.value}${intrinsic_h.unit}`,
    to: `${new_w}pxx${new_h}px`,
  };
}

/**
 * Format a length to match the existing on-disk convention:
 * trailing-zero-stripped to 3dp, with at least one decimal place
 * (so `768` -> `"768.0"`, `577.194` -> `"577.194"`).
 *
 * @param {number} n Numeric length in px.
 * @returns {string}
 */
function fmt_length(n) {
  const s = n.toFixed(3).replace(/0+$/, '');
  return s.endsWith('.') ? s + '0' : s;
}

/**
 * Strip the legacy internal dark-mode `<style>` block injected by an
 * older normalization pass. The current site uses an external CSS
 * rule tied to the `.dark` class instead. Returns `{ changed: false }`
 * if the SVG never carried that block.
 *
 * @param {string} svg Raw SVG source.
 * @returns {{ svg: string, changed: boolean }}
 */
function strip_legacy_dark_style(svg) {
  if (!LEGACY_DARK_STYLE_RE.test(svg)) return { svg, changed: false };
  return { svg: svg.replace(LEGACY_DARK_STYLE_RE, ''), changed: true };
}
