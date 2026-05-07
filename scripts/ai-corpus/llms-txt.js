import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, dirname, join, relative } from 'node:path';
import {
  stripMarkdownInline as strip_md_inline,
  titleCase as title_case,
} from '../shared/markdown.mjs';

const SITE_NAME = 'XPower Banq';
const SITE_TAGLINE = 'Permissionless DeFi lending on Avalanche — locked positions, lethargic governance, capital-efficient liquidation.';

// Order mirrors the user-journey reading order documented in CLAUDE.md.
// Anything not listed here falls into a trailing "Other" section so new
// top-level directories don't go silently missing.
const SECTION_ORDER = [
  ['introduction',       'Introduction'],
  ['concepts',           'Concepts'],
  ['features',           'Features'],
  ['using-the-protocol', 'Using the protocol'],
  ['for-developers',     'For developers'],
  ['for-keepers',        'For keepers'],
  ['governance',         'Governance'],
  ['risks',              'Risks'],
  ['security',           'Security'],
  ['parameters',         'Parameters'],
  ['reference',          'Reference'],
  ['research',           'Research'],
];

/**
 * Emits the two `/llms*.txt` artifacts that AI tooling fetches when a
 * user (or a developer integration) asks an assistant to ingest these
 * docs. `llms.txt` is a sectioned link index following the llmstxt.org
 * spec; `llms-full.txt` is the full Markdown corpus concatenated for
 * single-fetch ingestion. Both are derived from the same `Blocks` walk
 * that feeds the Ask-AI worker, so the three artifacts stay in sync.
 */
export class LlmsTxt {
  /**
   * @param {string[]} blocks Formatted `## FILE: /url` blocks in output order.
   * @param {string} content_root Absolute path of the docs root.
   * @param {string} index_path Absolute path to write `llms.txt` to.
   * @param {string} full_path Absolute path to write `llms-full.txt` to.
   * @param {string} repo_root Absolute repo root, used for the summary log.
   * @param {string} site_url Canonical site URL (no trailing slash) used
   *   to absolutize the per-page links in the index file.
   */
  constructor(blocks, content_root, index_path, full_path, repo_root, site_url) {
    this.blocks = blocks;
    this.content_root = content_root;
    this.index_path = index_path;
    this.full_path = full_path;
    this.repo_root = repo_root;
    this.site_url = site_url.replace(/\/+$/, '');
    this.index_text = '';
    this.full_text = '';
  }

  /**
   * Build the two artifacts in memory and persist them to disk.
   *
   * @returns {Promise<void>}
   */
  async io_write() {
    this.index_text = await this.#format_index();
    this.full_text = this.#format_full();
    await mkdir(dirname(this.index_path), { recursive: true });
    await writeFile(this.index_path, this.index_text);
    await writeFile(this.full_path, this.full_text);
  }

  /**
   * Log one line per artifact (KiB / file or entry count).
   *
   * @param {string} tag Prefix for each log line.
   * @returns {void}
   */
  log_summary(tag) {
    const i_bytes = Buffer.byteLength(this.index_text, 'utf8');
    const f_bytes = Buffer.byteLength(this.full_text, 'utf8');
    const i_rel = relative(this.repo_root, this.index_path);
    const f_rel = relative(this.repo_root, this.full_path);
    console.log(tag, `${i_rel} ${(i_bytes / 1024).toFixed(1)} KiB, ${this.blocks.length} entries`);
    console.log(tag, `${f_rel} ${(f_bytes / 1024).toFixed(1)} KiB, ${this.blocks.length} files`);
  }

  /**
   * Build the `llms.txt` index — H1, blockquote tagline, then one `## Section`
   * per top-level `content/` directory, each containing a bulleted list of
   * `[Title](absolute-url): description` entries (llmstxt.org spec).
   *
   * @returns {Promise<string>}
   */
  async #format_index() {
    const pages = await this.#read_page_index();
    const sections = group_pages_by_section(pages);
    const lines = [
      `# ${SITE_NAME}`,
      '',
      `> ${SITE_TAGLINE}`,
      '',
    ];
    for (const [slug, label] of SECTION_ORDER) {
      const items = sections.get(slug);
      if (!items || items.length === 0) continue;
      lines.push(`## ${label}`, '');
      for (const item of items) {
        const desc = item.description ? `: ${item.description}` : '';
        lines.push(`- [${item.title}](${this.site_url}${item.url})${desc}`);
      }
      lines.push('');
      sections.delete(slug);
    }
    // Anything left over — keeps new top-level dirs discoverable without code edits.
    for (const [slug, items] of sections) {
      if (items.length === 0) continue;
      lines.push(`## ${title_case(slug)}`, '');
      for (const item of items) {
        const desc = item.description ? `: ${item.description}` : '';
        lines.push(`- [${item.title}](${this.site_url}${item.url})${desc}`);
      }
      lines.push('');
    }
    return lines.join('\n').replace(/\n+$/, '\n');
  }

  /**
   * Build the `llms-full.txt` artifact — exactly the same shape as
   * `ai-corpus.md` so AI tooling that already understands the worker
   * bundle can also consume the public file. The header differs only in
   * dropping the trailing "corpus" word.
   *
   * @returns {string}
   */
  #format_full() {
    return `# ${SITE_NAME} documentation\n\n${this.blocks.join('\n---\n\n')}`;
  }

  /**
   * Re-read each page's source to extract title + first-paragraph
   * description for the index. We do this rather than parsing the
   * already-formatted `## FILE:` blocks so the index entries match the
   * exact human-authored title (first H1) rather than the synthetic
   * `## FILE:` header.
   *
   * @returns {Promise<Array<{url: string, title: string, description: string}>>}
   */
  async #read_page_index() {
    const out = [];
    for (const block of this.blocks) {
      const m = /^## FILE: (\/\S+)\n\n([\s\S]*)$/.exec(block);
      if (!m) continue;
      const [, url, body] = m;
      const { title, description } = extract_title_and_lede(body);
      out.push({ url, title: title || derive_title_from_url(url), description });
    }
    return out;
  }
}

/**
 * Group page-index entries by their top-level directory slug (the first
 * path segment after the leading slash).
 *
 * @param {Array<{url: string, title: string, description: string}>} pages
 * @returns {Map<string, Array<{url: string, title: string, description: string}>>}
 */
function group_pages_by_section(pages) {
  const sections = new Map();
  for (const p of pages) {
    const slug = p.url.split('/').filter(Boolean)[0] ?? '';
    if (!sections.has(slug)) sections.set(slug, []);
    sections.get(slug).push(p);
  }
  return sections;
}

/**
 * Pull the first H1 (title) and first prose paragraph (description) from
 * a markdown body whose frontmatter has already been stripped. Returns
 * empty strings when nothing usable is found — callers decide the
 * fallback.
 *
 * @param {string} body Markdown body with frontmatter removed.
 * @returns {{title: string, description: string}}
 */
function extract_title_and_lede(body) {
  const lines = body.split(/\n/);
  let title = '';
  let description = '';
  let in_title = false;
  for (const raw of lines) {
    const line = raw.trim();
    if (!title) {
      const m = /^#\s+(.+?)\s*$/.exec(line);
      if (m) { title = strip_md_inline(m[1]); in_title = true; continue; }
    }
    if (in_title && !line) continue;
    if (!line) continue;
    if (/^(#|<|::|\||!\[|\[|>|`{3}|---)/.test(line)) continue;
    if (line.length < 40) continue;
    description = strip_md_inline(line).slice(0, 200);
    break;
  }
  return { title, description };
}

function derive_title_from_url(url) {
  const seg = url.split('/').filter(Boolean).pop() ?? '';
  return title_case(seg);
}
