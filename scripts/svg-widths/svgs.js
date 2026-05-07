import { readdir } from 'node:fs/promises';
import { join } from 'node:path';

/**
 * The list of `.svg` paths under an asset tree, plus the discovery
 * config that produced them. Construction stores config; `io_read()`
 * walks the tree and populates `list` in deterministic order.
 */
export class Svgs {
  /**
   * @param {string} root_path Absolute path of the asset root.
   * @param {Set<string>} skip_dirs Directory basenames to prune.
   */
  constructor(
    root_path, skip_dirs,
  ) {
    this.root_path = root_path;
    this.skip_dirs = skip_dirs;
    /** @type {string[]} Discovered `.svg` paths; populated by io_read(). */
    this.list = [];
  }

  /**
   * Walk `root_path` and populate `this.list` with every `.svg` file
   * (sorted), pruning directories whose basename appears in
   * `skip_dirs`. Idempotent.
   *
   * @returns {Promise<void>}
   */
  async io_read() {
    this.list = await walk(
      this.root_path, (n) => n.toLowerCase().endsWith('.svg'), this.skip_dirs,
    );
  }
}

/**
 * Recursively collect every regular file under `dir` for which
 * `accept` returns true, skipping any directory whose basename appears
 * in `skip_dirs` and any dotfile/dotdir. Returns absolute paths sorted
 * in lexicographic order so processing is deterministic.
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
