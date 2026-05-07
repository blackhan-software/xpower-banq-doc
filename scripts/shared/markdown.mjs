/**
 * Shared markdown-text helpers used by both the VitePress config
 * (`.vitepress/config/seo/*`) and the AI-corpus bundler (`scripts/ai-corpus/*`).
 *
 * These four functions were previously duplicated byte-for-byte across those
 * two contexts. They are pure (no I/O) and intentionally tiny so they can run
 * in both the Node CLI scripts and the esbuild-bundled VitePress config.
 *
 * The first-paragraph / lede extractors are deliberately NOT hoisted here: the
 * config and the corpus bundler skip different line prefixes and slice to
 * different lengths, so they keep their own loops and only borrow the helpers
 * below.
 */

/**
 * Strip a leading YAML frontmatter block (delimited by `---` lines) from a
 * markdown string and trim surrounding whitespace. Returns the input trimmed
 * if no frontmatter is present.
 *
 * @param {string} md Raw markdown source, possibly with frontmatter.
 * @returns {string} Markdown body with frontmatter and outer whitespace removed.
 */
export function stripFrontmatter(md) {
  return md.replace(/^---\n[\s\S]*?\n---\n?/, '').trim();
}

/**
 * Remove inline markdown decorations (links, inline code, bold, italic,
 * underscore emphasis) and collapse runs of whitespace. Used to flatten a
 * single line of prose into plain text for meta descriptions and lede lines.
 *
 * @param {string} s A single line (or short run) of markdown.
 * @returns {string} Plain text with inline markup stripped.
 */
export function stripMarkdownInline(s) {
  return s
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/_([^_]+)_/g, '$1')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Convert a kebab/snake slug into Title Case.
 *
 * @param {string} slug e.g. `time-locks`.
 * @returns {string} e.g. `Time Locks`.
 */
export function titleCase(slug) {
  return slug.replace(/[-_]+/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Convert an arbitrary string into a URL-safe anchor slug.
 *
 * @param {string} s Arbitrary text.
 * @returns {string} Lowercase, alphanumerics joined by single dashes.
 */
export function slugify(s) {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
