import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:5000'
    }
  },
  esbuild: {
    loader: 'jsx',
    include: /src\/.*\.[jt]sx?$/,
    exclude: [],
  }
})
