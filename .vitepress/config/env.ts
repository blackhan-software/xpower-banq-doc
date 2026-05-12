import { loadEnv } from 'vite'

// Single source of build-time env resolution for the VitePress config.
// Previously nav.ts, head.ts, and seo.ts each called loadEnv() independently
// and re-derived the same URLs; they now all read from here.
//
// `VITE_`-prefixed vars are also exposed to the client bundle via vite.ts's
// envPrefix; the unprefixed BANQ_* vars are build-time only (baked into the
// static HTML / head config).
const env = loadEnv(process.env.NODE_ENV ?? '', process.cwd(), '')

export const appUrl = env.BANQ_APP_URL ?? ''
export const paperUrl = env.BANQ_PAPER_URL ?? ''
export const aiWorkerUrl = env.VITE_AI_WORKER_URL ?? ''

// Canonical hostname for SEO (sitemap, canonical links, OG/JSON-LD URLs),
// with any trailing slashes stripped so callers can append `/${slug}`.
export const wwwUrl = (env.BANQ_WWW_URL ?? '').replace(/\/+$/, '')
