import { mkdir, writeFile } from 'node:fs/promises';
import { basename, dirname, relative } from 'node:path';

/**
 * The assembled documentation corpus together with the metadata needed
 * to persist and describe it. Construction is the assembly step; the
 * two instance methods cover the only two side effects (`io_write` to
 * disk, `log_summary` to stdout).
 */
export class Corpus {
  /**
   * Build a new corpus by joining per-page `## FILE:` blocks under the
   * single docs-corpus header. The constructor is the assembler — no
   * separate factory because the join is one line.
   *
   * @param {string[]} blocks Formatted `## FILE:` blocks in output order.
   * @param {string} dest_path Absolute destination path on disk.
   * @param {string} repo_root Absolute repo root, used to render a
   *   relative path in the summary line.
   */
  constructor(blocks, dest_path, repo_root) {
    this.text = `# XPower Banq documentation corpus\n\n${blocks.join('\n---\n\n')}`;
    this.file_count = blocks.length;
    this.dest_path = dest_path;
    this.repo_root = repo_root;
  }

  /**
   * Persist the corpus to `dest_path`, creating the parent directory if
   * needed.
   *
   * @returns {Promise<void>}
   */
  async io_write() {
    await mkdir(dirname(this.dest_path), { recursive: true });
    await writeFile(this.dest_path, this.text);
  }

  /**
   * Log a one-line size summary (KiB / token estimate / file count) and
   * emit a warning when the estimate exceeds Sonnet 4.6's 200K standard
   * input window.
   *
   * @returns {void}
   */
  log_summary(tag) {
    const bytes = Buffer.byteLength(this.text, 'utf8');
    const tokens = Math.round(bytes / 4); // rough — 4 chars/token average
    const rel_path = relative(this.repo_root, this.dest_path);
    console.log(
      tag, `${rel_path} ${(bytes / 1024).toFixed(1)} KiB (~${tokens.toLocaleString()} tokens), ${this.file_count} files`
    );
    if (tokens > 200_000) {
      console.warn(tag, "corpus exceeds 200K tokens");
    }
  }
}
