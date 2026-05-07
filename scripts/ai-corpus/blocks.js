import { readdir, readFile } from 'node:fs/promises';
import { join, relative } from 'node:path';
import { stripFrontmatter } from '../shared/markdown.mjs';

/**
 * The list of `## FILE: /url` blocks for a docs tree, plus the discovery
 * config that produced them. Construction stores config; `io_read()`
 * walks the tree and populates `list` in deterministic order.
 */
export class Blocks {
  /**
   * @param {string} content_root Absolute path of the docs root.
   * @param {Set<string>} skip_basenames File basenames to exclude.
   * @param {Set<string>} skip_dirs Directory basenames to prune.
   */
  constructor(
    content_root, skip_basenames, skip_dirs,
  ) {
    this.content_root = content_root;
    this.skip_basenames = skip_basenames;
    this.skip_dirs = skip_dirs;
    /** @type {string[]} Formatted `## FILE:` blocks; populated by io_read(). */
    this.list = [];
  }

  /**
   * Walk `content_root`, format each accepted page as a `## FILE:` block,
   * and store the non-empty ones in `this.list` (replacing any previous
   * contents). Idempotent.
   *
   * @returns {Promise<void>}
   */
  async io_read() {
    const files = await find_pages(
      this.content_root, this.skip_basenames, this.skip_dirs,
    );
    const out = [];
    for (const file of files) {
      const block = await format_page(file, this.content_root);
      if (block) out.push(block);
    }
    this.list = out;
  }
}

/**
 * Discover every documentation page under `content_root`: any `.md` file
 * whose basename is not in `skip_basenames`, pruning directories whose
 * basename is in `skip_dirs`. Wraps `walk` with the doc-specific accept
 * predicate so the caller never has to spell it out.
 *
 * @param {string} content_root Absolute path of the docs root.
 * @param {Set<string>} skip_basenames File basenames to exclude.
 * @param {Set<string>} skip_dirs Directory basenames to prune.
 * @returns {Promise<string[]>} Sorted absolute paths of discovered pages.
 */
async function find_pages(
  content_root, skip_basenames, skip_dirs,
) {
  return walk(
    content_root, (n) => n.endsWith('.md') && !skip_basenames.has(n), skip_dirs,
  );
}

/**
 * Read one markdown page and convert it into a single citable block:
 * `## FILE: /url\n\n<body>\n` where `/url` is the page's path under
 * `content_root` with the `.md` extension stripped. Returns `null` for
 * empty bodies (after frontmatter removal) so the caller can drop them.
 *
 * @param {string} file Absolute path of the markdown file.
 * @param {string} content_root Absolute path of the docs root, used to derive the URL.
 * @returns {Promise<string | null>} Formatted block, or `null` if the body is empty.
 */
async function format_page(
  file, content_root,
) {
  const url = '/' + relative(content_root, file).replace(/\\/g, '/').replace(/\.md$/, '');
  const body = stripFrontmatter(await readFile(file, 'utf8'));
  return body ? `## FILE: ${url}\n\n${body}\n` : null;
}

/**
 * Recursively collect every regular file under `dir` for which `accept`
 * returns true, skipping any directory whose basename appears in
 * `skip_dirs` and any dotfile/dotdir. Returns absolute paths sorted in
 * lexicographic order so the bundle output is deterministic.
 *
 * @param {string} dir Directory to start walking from.
 * @param {(name: string) => boolean} accept Filter applied to file basenames.
 * @param {Set<string>} [skip_dirs] Basenames of directories to prune.
 * @returns {Promise<string[]>} Sorted absolute paths of accepted files.
 */
async function walk(
  dir, accept, skip_dirs = new Set(),
) {
  const list = [];
  let entries;
  try {
    entries = await readdir(dir, { withFileTypes: true });
  } catch {
    return list;
  }
  for (const entry of entries) {
    if (entry.name.startsWith('.')) continue;
    if (skip_dirs.has(entry.name)) continue;
    const full_name = join(dir, entry.name);
    if (entry.isDirectory()) {
      list.push(...await walk(full_name, accept, skip_dirs));
      continue;
    }
    if (entry.isFile() && accept(entry.name)) {
      list.push(full_name);
      continue;
    }
  }
  return list.sort();
}
