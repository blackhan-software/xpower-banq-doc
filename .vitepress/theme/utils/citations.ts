const CORPUS_SECTION = /^\/(introduction|concepts|features|using-the-protocol|for-developers|for-keepers|governance|parameters|risks|security|research|reference)\//

function normalizeCitationURL(url: string): string {
  const u = url.replace(/^https?:\/\/[^/]+\//, '/')
  if (!CORPUS_SECTION.test(u)) return url
  return u.replace(/\.md(#.*)?$/, '$1')
}

export function normalizeCitations(text: string): string {
  return text.replace(/(\]\()([^)\s]+)(\))/g, (_m, o, u, c) => `${o}${normalizeCitationURL(u)}${c}`)
}
