import { defineConfig } from 'vite'
import { devtools } from '@tanstack/devtools-vite'

import { tanstackStart } from '@tanstack/react-start/plugin/vite'

import viteReact, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import tailwindcss from '@tailwindcss/vite'

const allowedHosts = process.env.ALLOWED_HOSTS 
  ? process.env.ALLOWED_HOSTS.split(',').map(h => h.trim()) 
  : ['localhost'];

const config = defineConfig({
  resolve: { tsconfigPaths: true },
  server: {
    allowedHosts: allowedHosts,
  },
  preview: {
    allowedHosts: allowedHosts,
  },
  plugins: [
    devtools(),
    tailwindcss(),
    tanstackStart({
      spa: { enabled: true },
    }),
    viteReact(),
    babel({ presets: [reactCompilerPreset()] }),
  ],
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        }
      }
    }
  }
})

export default config
