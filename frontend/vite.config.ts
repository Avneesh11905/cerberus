import { defineConfig, loadEnv } from 'vite' // trigger reload
import { devtools } from '@tanstack/devtools-vite'

import { tanstackStart } from '@tanstack/react-start/plugin/vite'

import viteReact from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {
  // Load env variables from .env files
  const env = loadEnv(mode, process.cwd(), '')

  return {
    resolve: { tsconfigPaths: true },
    server: {
      allowedHosts: env.ALLOWED_HOSTS
        ? env.ALLOWED_HOSTS.split(',')
        : undefined,
    },
    optimizeDeps: {
      include: ['react', 'react-dom', '@tanstack/react-router', 'lucide-react'],
    },
    plugins: [
      devtools(),
      tailwindcss(),
      tanstackStart(),
      viteReact(),
    ],
  }
})
