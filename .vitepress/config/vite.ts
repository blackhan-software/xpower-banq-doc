import { fileURLToPath } from 'node:url'
import type { UserConfig } from 'vitepress'

export const vite: UserConfig['vite'] = {
  envDir: fileURLToPath(new URL('../..', import.meta.url)),
  envPrefix: ['VITE_'],
  build: {
    chunkSizeWarningLimit: 4096,
  },
  server: {
    allowedHosts: ['www.xpowerbanq.com'],
    host: '0.0.0.0',
    port: 5174,
  },
}
